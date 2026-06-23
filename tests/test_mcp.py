"""Contrato MCP: o loop sem humano precisa de leitura (resource) E escrita (tools).
Cobre também a escolha de backend (local/remoto) e que a escrita continua HITL."""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx                         # noqa: E402
import lifeline.mcp_server as srv     # noqa: E402
from lifeline import cli             # noqa: E402
from lifeline.mcp_server import mcp  # noqa: E402


class TestMCPContract(unittest.IsolatedAsyncioTestCase):
    async def test_write_tools_registered(self):
        names = [t.name for t in await mcp.list_tools()]
        self.assertIn("lifeline_append", names)           # escrita: anexar
        self.assertIn("lifeline_recontextualize", names)  # escrita: supersede
        self.assertIn("lifeline_recall", names)           # leitura: relevância

    async def test_context_resource_registered(self):
        uris = [str(r.uri) for r in await mcp.list_resources()]
        uris += [t.uriTemplate for t in await mcp.list_resource_templates()]
        self.assertTrue(any("lifeline://project/context" in u for u in uris))

    def test_healthz_route_registered(self):
        # health check (Render/Railway) + checagem no navegador → GET /healthz deve existir
        paths = {getattr(r, "path", "") for r in mcp.streamable_http_app().routes}
        self.assertIn("/healthz", paths)

    def test_instructions_cover_bootstrap(self):
        # AI-first: a IA que conecta a uma line vazia precisa saber fazer o checkpoint HITL
        text = srv._INSTRUCTIONS
        self.assertIn("BOOTSTRAP", text.upper())
        self.assertIn("granular", text.lower())          # entradas granulares (não bloco único)
        self.assertIn("never infer", text.lower())        # guardrail: não inferir do código

    def test_instructions_pin_append_only_loop_and_hitl(self):
        # THE responsible surface: every connecting AI must be TOLD, deterministically (FastMCP
        # ships this in `initialize`), that (a) the ledger is append-only, (b) it PROPOSES on each
        # meaningful unit of work, and (c) writes are HITL — a human gates them, the AI never writes
        # truth. Regression-lock the wording so a future edit can't silently drop the contract.
        t = srv._INSTRUCTIONS.lower()
        self.assertIn("append-only", t)                   # the model itself (Law #2)
        self.assertIn("propose", t)                       # the verb — never "write the truth"
        self.assertIn("each meaningful", t)               # the per-decision/feature/fix/incident loop
        self.assertIn("human approves", t)                # HITL: a human gates every write
        # the tools repeat the contract at point-of-use (what the AI reads when about to write)
        self.assertIn("PENDING", srv.lifeline_append.__doc__)
        self.assertIn("HITL", srv.lifeline_append.__doc__)
        self.assertIn("Law #2", srv.lifeline_recontextualize.__doc__)   # append-only, never an edit


class TestMCPBackendAndHITL(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))

    def test_configure_selects_backend_from_env(self):
        with mock.patch.dict(os.environ, {"LIFELINE_STORE": "supabase", "LIFELINE_LINE": "research"}):
            srv._configure()
        self.assertEqual(cli._STORE["kind"], "supabase")    # modo nuvem (remoto) escolhido por env
        self.assertEqual(cli._STORE["line"], "research")

    def test_configure_defaults_to_sqlite(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            srv._configure()
        self.assertEqual(cli._STORE["kind"], "sqlite")      # local por padrão (sem regressão)

    async def test_append_tool_is_hitl(self):
        # a tool de escrita PROPÕE (fila pendente), NÃO commita direto na line (HITL)
        cli._STORE.update(kind="sqlite", line="ledger")
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        self.addCleanup(setattr, srv, "_DB", srv._DB)        # restaura o _DB original
        db = os.path.join(d, ".lifeline", "ledger.db")
        srv._DB = db
        msg = await srv.lifeline_append("decision", "usar gRPC", "porque escala")
        self.assertIn("PENDING", msg)
        self.assertEqual(len(await cli.cmd_review(db)), 1)   # entrou na fila…
        _, n, _t, _d = await cli.cmd_verify(db)
        self.assertEqual(n, 0)                                # …e NÃO na line (0 entradas seladas)

    async def test_handlers_read_the_line(self):
        # executa os handlers de LEITURA (project_context, lifeline_recall) contra um store real
        from lifeline.store import SQLiteEventStore
        from lifeline.entry import Entry
        cli._STORE.update(kind="sqlite", line="ledger")
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        self.addCleanup(setattr, srv, "_DB", srv._DB)
        db = os.path.join(d, ".lifeline", "ledger.db")
        os.makedirs(os.path.dirname(db))
        srv._DB = db
        s = SQLiteEventStore(db)
        await s.initialize()
        await s.append(Entry(kind="bootstrap", author="a", summary="Funda Z", body="why"))
        await s.append(Entry(kind="decision", author="a", summary="use SQLite", body="simple"))

        ctx = await srv.project_context()                     # resource montado
        self.assertIn("Funda Z", ctx)
        self.assertIn("use SQLite", ctx)
        self.assertIn("use SQLite", await srv.lifeline_recall("sqlite"))         # recall acha
        self.assertIn("Nothing relevant", await srv.lifeline_recall("zzqxyznada"))  # sem match → mensagem vazia

    async def test_request_store_factory_seam(self):
        # costura p/ o hub injetar tenancy (team-line) SEM forkar: o factory tem prioridade
        self.addCleanup(setattr, srv, "_REQUEST_STORE_FACTORY", None)
        called = {}
        async def factory(token):
            called["token"] = token
            return "hub-store"
        srv._REQUEST_STORE_FACTORY = factory
        self.assertEqual(await srv._open_request(), "hub-store")   # usou o factory
        self.assertIn("token", called)                            # e passou o token (None fora de auth)


class TestOAuthResourceServer(unittest.IsolatedAsyncioTestCase):
    def _verifier(self, handler):
        return srv.SupabaseTokenVerifier(url="https://proj.supabase.co", key="anon",
                                         transport=httpx.MockTransport(handler))

    async def test_valid_token_returns_access_token(self):
        seen = []

        def handler(req):
            seen.append(req)
            return httpx.Response(200, json={"id": "user-123", "email": "a@b.c"})

        at = await self._verifier(handler).verify_token("jwt-xyz")
        self.assertIsNotNone(at)
        self.assertEqual(at.token, "jwt-xyz")        # carrega o JWT p/ escopar a RLS por usuário
        self.assertEqual(at.client_id, "user-123")   # user id do Supabase
        req = seen[0]
        self.assertTrue(str(req.url).endswith("/auth/v1/user"))
        self.assertEqual(req.headers["apikey"], "anon")
        self.assertEqual(req.headers["authorization"], "Bearer jwt-xyz")

    async def test_invalid_token_returns_none(self):
        at = await self._verifier(lambda req: httpx.Response(401, json={"msg": "bad"})).verify_token("nope")
        self.assertIsNone(at)                         # 401 → rejeitado

    async def test_missing_config_returns_none(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            v = srv.SupabaseTokenVerifier()           # sem url/key
        self.assertIsNone(await v.verify_token("whatever"))

    async def test_jwks_verifier_accepts_valid_rejects_bad(self):
        # #0049 trocou o AS próprio pelo OAuth Server do Supabase → validamos por JWKS/ES256.
        import time
        import jwt
        from cryptography.hazmat.primitives.asymmetric import ec
        priv = ec.generate_private_key(ec.SECP256R1())
        ISS = "https://proj.supabase.co/auth/v1"

        class _FakeJWK:   # mimetiza jwt.PyJWKClient
            def get_signing_key_from_jwt(self, token):
                return type("K", (), {"key": priv.public_key()})()

        v = srv.SupabaseJWKSVerifier(url="https://proj.supabase.co", _jwk_client=_FakeJWK())
        self.assertEqual(v.issuer, ISS)

        good = jwt.encode({"iss": ISS, "sub": "user-7", "exp": int(time.time()) + 3600},
                          priv, algorithm="ES256")
        at = await v.verify_token(good)
        self.assertIsNotNone(at)
        self.assertEqual(at.client_id, "user-7")           # sub vira o id (escopo RLS)
        self.assertEqual(at.token, good)                    # token original preservado p/ a RLS

        expired = jwt.encode({"iss": ISS, "sub": "u", "exp": int(time.time()) - 10},
                             priv, algorithm="ES256")
        self.assertIsNone(await v.verify_token(expired))    # expirado → 401

        wrong_iss = jwt.encode({"iss": "https://evil.example/auth/v1", "sub": "u",
                                "exp": int(time.time()) + 3600}, priv, algorithm="ES256")
        self.assertIsNone(await v.verify_token(wrong_iss))  # issuer errado → 401
        self.assertIsNone(await v.verify_token(""))         # vazio → None
        self.assertIsNone(await v.verify_token("garbage"))  # lixo → None (sem estourar)

    def test_build_remote_with_oauth_serves_metadata(self):
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        env = {"LIFELINE_OAUTH": "1", "LIFELINE_STORE": "supabase",
               "SUPABASE_URL": "https://proj.supabase.co", "SUPABASE_KEY": "anon"}
        with mock.patch.dict(os.environ, env):
            srv._configure()
            server = srv._build_remote()
        self.assertIsNotNone(server.settings.auth)    # virou Resource Server
        paths = {getattr(r, "path", "") for r in server.sse_app().routes}
        self.assertTrue(any("oauth-protected-resource" in p for p in paths), paths)  # discovery

    def test_build_remote_without_oauth_is_authless(self):
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        with mock.patch.dict(os.environ, {}, clear=True):
            srv._configure()
            server = srv._build_remote()
        self.assertIsNone(server.settings.auth)       # sem OAuth → authless

    async def test_jwks_audience_pinning_is_opt_in(self):
        # S2: with no LIFELINE_OAUTH_AUDIENCE the verifier accepts any aud (issuer guards origin);
        # once an audience is pinned, a token minted for a different resource is rejected here.
        import time
        import jwt
        from cryptography.hazmat.primitives.asymmetric import ec
        priv = ec.generate_private_key(ec.SECP256R1())
        ISS = "https://proj.supabase.co/auth/v1"

        class _FakeJWK:
            def get_signing_key_from_jwt(self, token):
                return type("K", (), {"key": priv.public_key()})()

        def tok(aud=None):
            claims = {"iss": ISS, "sub": "u", "exp": int(time.time()) + 3600}
            if aud is not None:
                claims["aud"] = aud
            return jwt.encode(claims, priv, algorithm="ES256")

        off = srv.SupabaseJWKSVerifier(url="https://proj.supabase.co", _jwk_client=_FakeJWK())
        self.assertIsNotNone(await off.verify_token(tok(aud="anything")))   # default: aud ignored
        self.assertIsNotNone(await off.verify_token(tok()))                 # no aud claim → fine

        pinned = srv.SupabaseJWKSVerifier(url="https://proj.supabase.co", _jwk_client=_FakeJWK(),
                                          audience="authenticated")
        self.assertIsNotNone(await pinned.verify_token(tok(aud="authenticated")))  # match → ok
        self.assertIsNone(await pinned.verify_token(tok(aud="other-resource")))    # mismatch → 401
        self.assertIsNone(await pinned.verify_token(tok()))                        # missing aud → 401

    def test_as_refuses_password_form_on_public_deploy(self):
        # S3: a public AS deploy with no social provider must REFUSE to expose the dev-only ROPC form
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        env = {"LIFELINE_OAUTH_AS": "1", "LIFELINE_STORE": "supabase",
               "SUPABASE_URL": "https://proj.supabase.co", "SUPABASE_KEY": "anon",
               "LIFELINE_MCP_PUBLIC_URL": "https://mcp.example"}   # public, no provider, no override
        with mock.patch.dict(os.environ, env, clear=True):
            srv._configure()
            with self.assertRaises(SystemExit):
                srv._build_remote()

    def test_as_password_form_allowed_with_explicit_override(self):
        # S3: the override turns ROPC back on (with a warning), for a deliberate dev/self-host choice
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        env = {"LIFELINE_OAUTH_AS": "1", "LIFELINE_STORE": "supabase",
               "SUPABASE_URL": "https://proj.supabase.co", "SUPABASE_KEY": "anon",
               "LIFELINE_MCP_PUBLIC_URL": "https://mcp.example", "LIFELINE_OAUTH_ALLOW_PASSWORD": "1"}
        with mock.patch.dict(os.environ, env, clear=True):
            srv._configure()
            server = srv._build_remote()
        self.assertIsNotNone(server.settings.auth)        # built as an AS

    def test_as_hosted_provider_needs_no_override(self):
        # S3: a social provider IS the production path — no refusal, no override needed
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        env = {"LIFELINE_OAUTH_AS": "1", "LIFELINE_STORE": "supabase",
               "SUPABASE_URL": "https://proj.supabase.co", "SUPABASE_KEY": "anon",
               "LIFELINE_MCP_PUBLIC_URL": "https://mcp.example", "LIFELINE_OAUTH_PROVIDER": "github"}
        with mock.patch.dict(os.environ, env, clear=True):
            srv._configure()
            server = srv._build_remote()
        self.assertIsNotNone(server.settings.auth)

    def test_build_remote_oauth_requested_but_unconfigured_falls_back_authless(self):
        # C4: OAuth requested but no Supabase env → must degrade to AUTHLESS (loudly), never crash
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        with mock.patch.dict(os.environ, {"LIFELINE_OAUTH": "1"}, clear=True):
            srv._configure()
            server = srv._build_remote()
        self.assertIsNone(server.settings.auth)           # fell back to authless (anti-silent gap)

    def test_transport_security_allows_configured_host(self):
        with mock.patch.dict(os.environ, {"LIFELINE_MCP_ALLOWED_HOSTS": "x.trycloudflare.com,meu.app"}):
            ts = srv._transport_security()
        self.assertTrue(ts.enable_dns_rebinding_protection)   # proteção ON com lista
        self.assertIn("x.trycloudflare.com", ts.allowed_hosts)
        self.assertIn("meu.app:*", ts.allowed_hosts)

    def test_transport_security_strips_scheme_from_host(self):
        # erro comum: colar ALLOWED_HOSTS com https:// → sem normalizar, o Host header não casa (421)
        with mock.patch.dict(os.environ, {"LIFELINE_MCP_ALLOWED_HOSTS": "https://app.onrender.com/"}):
            ts = srv._transport_security()
        self.assertIn("app.onrender.com", ts.allowed_hosts)            # host puro extraído
        self.assertNotIn("https://app.onrender.com", ts.allowed_hosts)  # esquema removido

    def test_transport_security_derives_host_from_render_env(self):
        with mock.patch.dict(os.environ, {"RENDER_EXTERNAL_HOSTNAME": "lifeline-cnah.onrender.com"}, clear=True):
            ts = srv._transport_security()
        self.assertIn("lifeline-cnah.onrender.com", ts.allowed_hosts)   # Render injeta sozinho

    def test_transport_security_default_disables_protection(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            ts = srv._transport_security()
        self.assertFalse(ts.enable_dns_rebinding_protection)  # túnel/proxy: host variável → libera


if __name__ == "__main__":
    unittest.main(verbosity=2)
