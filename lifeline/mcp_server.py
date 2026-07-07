"""Superfície MCP — a interface da IA é o produto (Lei #7).

  - LER ao conectar:  resource `lifeline://project/context` + tool `lifeline_recall`.
  - PROPOR ao trabalhar:  `lifeline_append` / `lifeline_recontextualize` — escrita HITL:
    vira PROPOSTA pendente; um humano aprova antes de entrar na line.

Três modos, mesma superfície (registrada por `_register`):
  - LOCAL (stdio, SQLite):   LIFELINE_DB=…  lifeline-mcp
  - REMOTO (HTTP/SSE, nuvem): LIFELINE_STORE=supabase  SUPABASE_URL/KEY/TOKEN=…  lifeline-mcp-remote
  - REMOTO + OAuth (multi-tenant): idem, e o servidor vira um OAuth Resource Server —
    valida o Bearer JWT de CADA requisição (Supabase) e escopa o store por usuário
    (RLS `owner=auth.uid()`). Liga com LIFELINE_OAUTH=1.

Honestidade (#0046/#0047): o Resource Server (validação de token + metadata de
protected-resource + multi-tenant) está pronto e testado aqui. O Authorization Server
completo (DCR + authorization-code) que os conectores claude.ai/ChatGPT/Gemini exigem
depende de um AS compatível — o Supabase Auth não é um AS OAuth genérico com DCR. Ver
docs/MCP_REMOTE.md.
"""
import asyncio
import logging
import os
from typing import Optional

import httpx
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import Icon

from lifeline.cli import _STORE, _open, _staging, _validate

_DB = os.environ.get("LIFELINE_DB", os.path.join(".lifeline", "ledger.db"))
_AUTHOR = os.environ.get("LIFELINE_AUTHOR", "mcp")

# Branding advertised in the `initialize` serverInfo (SEP-973): clients that support server icons
# render the Lifeline mark next to the connector. URLs are PUBLIC (the site) — PNG preferred + SVG.
# (Some hosts, incl. claude.ai today, still show a generic icon — that's a client-side gap, not ours.)
_WEBSITE = "https://lifelinecontext.com"
_ICONS = [
    Icon(src="https://lifelinecontext.com/assets/logo/lifeline-tile-512.png", mimeType="image/png", sizes=["512x512"]),
    Icon(src="https://lifelinecontext.com/assets/logo/lifeline-tile-1024.png", mimeType="image/png", sizes=["1024x1024"]),
    Icon(src="https://lifelinecontext.com/assets/favicon.svg", mimeType="image/svg+xml", sizes=["any"]),
]

# Manual de uso entregue a TODA IA que conecta (FastMCP envia no initialize). AI-first: a IA
# se onboarda sozinha, segue o loop, e sabe explicar/organizar pro humano.
_INSTRUCTIONS = (
    "Lifeline is this project's REASONING ledger (the *why*), append-only and content-addressed. "
    "ON CONNECT: read the `lifeline://project/context` resource FIRST — it's the assembled truth "
    "(what / why / decided / next); act from it. IF the context comes back EMPTY (a new line / an "
    "ongoing project with no history): offer to BOOTSTRAP — read the repo's reasoning artifacts "
    "(README, ADRs, PR descriptions, design docs), ask the human 3-7 *why* questions, and PROPOSE "
    "the checkpoint as GRANULAR entries (1 `bootstrap` + N `decision` + M `open`) via "
    "`lifeline_append` (HITL). NEVER infer the *why* from code/diffs. Use `lifeline_recall(query)` "
    "for 'did we already decide something about X?'. WHILE WORKING: on each meaningful "
    "decision/feature/fix/incident, PROPOSE via `lifeline_append(kind, summary, body)` — the body is "
    "the *why* (required). Reverted/updated something: `lifeline_recontextualize(parent_id, ...)`. "
    "You do NOT write the truth: writes are HITL — they enter as a PROPOSAL and a human "
    "approves/rejects. NEVER invent: every claim anchors to an entry. YOUR ROLE with the human: "
    "explain what Lifeline is, keep the context ORGANIZED (point out the decisions in force, flag "
    "closed threads, propose entries for the work done) — but the human curates. Don't accept junk."
)


def _configure() -> None:
    """Escolhe backend/line pelo ambiente (mesmo `_STORE` que a CLI usa em _open/_staging).

    LIFELINE_LINE vale TAMBÉM no modo local (SQLite): sem isto, o env documentado era um
    no-op fora da nuvem — o servidor abria sempre o db de LIFELINE_DB e ignorava a line
    (bug L1 da auditoria). Precedência: LIFELINE_DB explícito vence (aponta um arquivo
    exato); senão LIFELINE_LINE deriva `.lifeline/<line>.db` pelo MESMO mapeamento da CLI
    (resolve_paths — fonte única do nome→arquivo); senão o default `ledger`."""
    global _DB
    _STORE["kind"] = os.environ.get("LIFELINE_STORE", "sqlite")
    _STORE["line"] = os.environ.get("LIFELINE_LINE", "ledger")
    if os.environ.get("LIFELINE_DB"):
        _DB = os.environ["LIFELINE_DB"]
    elif os.environ.get("LIFELINE_LINE"):
        from lifeline.cli import resolve_paths
        _DB, _ = resolve_paths(os.environ["LIFELINE_LINE"], None, None)
    else:
        _DB = os.path.join(".lifeline", "ledger.db")


# ---- multi-tenant: token do usuário (do request OAuth) escopa o store por RLS -------------

def _request_token() -> Optional[str]:
    """JWT do usuário autenticado nesta requisição (None fora de contexto/sem auth)."""
    try:
        from mcp.server.auth.middleware.auth_context import get_access_token
        at = get_access_token()
        return at.token if at else None
    except Exception:
        logging.getLogger("lifeline.mcp").debug("sem contexto de auth na requisição", exc_info=True)
        return None


# Costura p/ hub/embedder: um factory de store POR REQUISIÇÃO (ex.: roteamento de team-line)
# pode ser injetado SEM forkar o core. Recebe o token do usuário e devolve o store; se setado,
# tem prioridade sobre a resolução padrão. (store: async/inicializado; staging: sync.)
_REQUEST_STORE_FACTORY = None     # Optional[Callable[[Optional[str]], Awaitable[EventStore]]]
_REQUEST_STAGING_FACTORY = None   # Optional[Callable[[Optional[str]], StagingStore]]


async def _open_request():
    """Store da requisição: na nuvem com token de usuário → escopa por RLS; senão, factory padrão.
    Um hub pode setar `_REQUEST_STORE_FACTORY` p/ adicionar tenancy (team-line) sem tocar no core."""
    tok = _request_token()
    if _REQUEST_STORE_FACTORY is not None:
        return await _REQUEST_STORE_FACTORY(tok)
    if _STORE["kind"] == "supabase" and tok:
        from lifeline.cloud import SupabaseEventStore
        s = SupabaseEventStore(line=_STORE["line"], token=tok)
        await s.initialize()
        return s
    return await _open(_DB)


def _staging_request():
    tok = _request_token()
    if _REQUEST_STAGING_FACTORY is not None:
        return _REQUEST_STAGING_FACTORY(tok)
    if _STORE["kind"] == "supabase" and tok:
        from lifeline.cloud import SupabaseStagingStore
        return SupabaseStagingStore(line=_STORE["line"], token=tok)
    return _staging(_DB)


# ---- handlers (registrados em qualquer instância FastMCP por _register) -------------------

async def project_context() -> str:
    """The project context, assembled and within budget — read this on connect."""
    from lifeline.context import ContextAssembler
    from lifeline.state import StateEngine
    store = await _open_request()
    return await ContextAssembler(StateEngine(store)).assemble()


async def lifeline_append(kind: str, summary: str, body: str = "",
                          agent: str = "mcp-agent", provider: str = "none",
                          model: str = "unknown") -> str:
    """PROPOSE an entry (decision/feature/fix/incident/milestone/note/open). It enters as PENDING —
    a human approves it via `lifeline review`/`approve` before it becomes part of the line (HITL).
    The *why* matters more than the *what* — state it in the body (required)."""
    try:
        _validate(kind, body)
    except ValueError as ex:
        return f"rejected: {ex}"
    staging = _staging_request()
    await staging.initialize()
    pid = await staging.propose(kind=kind, summary=summary, body=body, author=_AUTHOR,
                                agent=agent, provider=provider, model=model, parents=None)
    return f"proposal #{pid} queued ({kind}) — PENDING human approval (lifeline review)"


async def lifeline_recontextualize(parent_id: str, summary: str, body: str = "",
                                   agent: str = "mcp-agent", provider: str = "none",
                                   model: str = "unknown") -> str:
    """PROPOSE a correction that supersedes entry `parent_id` (reverted decision, closed thread,
    updated fact). Append-only, never an edit (Law #2). Stays PENDING until a human approves (HITL).
    State the *why* of the change in the body (required)."""
    try:
        _validate("correction", body)
    except ValueError as ex:
        return f"rejected: {ex}"
    staging = _staging_request()
    await staging.initialize()
    pid = await staging.propose(kind="correction", summary=summary, body=body, author=_AUTHOR,
                                agent=agent, provider=provider, model=model, parents=[parent_id])
    return f"correction proposal #{pid} (supersedes {parent_id[:12]}) — PENDING approval"


async def lifeline_recall(query: str, k: int = 5) -> str:
    """Retrieve the entries most RELEVANT to the current task (Layer 3 — anchored).
    Use it for "did we already decide something about X?" without reading the whole ledger.
    Relevance, not recency. REVERTED/closed hits come marked [REVERTED] (gap #G2) — don't act on
    dead truth."""
    from lifeline.recall import SemanticRecall, make_embedder
    from lifeline.state import StateEngine
    store = await _open_request()
    superseded = set((await StateEngine(store).reduce()).get("superseded", []))
    hits = await SemanticRecall(store, make_embedder()).search(query, k=k, superseded=superseded)
    if not hits:
        return "Nothing relevant found in the ledger."
    return "\n".join(
        f"[{h['kind']}]{' [REVERTED]' if h.get('superseded') else ''} {h['summary']} "
        f"(id={h['id'][:12]}, score={h['score']})" for h in hits
    )


async def _healthz(_request):
    """Liveness simples (GET 200) — health check de plataformas (Render/Railway) e checagem
    no navegador de que o servidor está no ar. Não expõe dado."""
    from starlette.responses import PlainTextResponse
    return PlainTextResponse("ok")


async def _oauth_consent(_request):
    """Serves the consent page for the Supabase OAuth-Server path, injecting SUPABASE_URL/KEY
    from the environment. Hosted by the server itself (the repo can stay PRIVATE — no GitHub
    Pages) and keeps the core GENERIC (no hardcoded project). The page ships INSIDE the wheel
    (`lifeline/templates/consent.html`), loaded via importlib.resources — so a `pip install`
    serves it without cloning the repo."""
    from importlib import resources
    from starlette.responses import HTMLResponse, PlainTextResponse
    try:
        html = (resources.files("lifeline") / "templates" / "consent.html").read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        return PlainTextResponse("consent page not bundled in this deploy", status_code=404)
    from lifeline.cloud import clean_url
    html = (html.replace("__LIFELINE_SUPABASE_URL__", clean_url(os.environ.get("SUPABASE_URL", "")))
                .replace("__LIFELINE_SUPABASE_ANON__", (os.environ.get("SUPABASE_KEY", "") or "").strip()))
    return HTMLResponse(html)


def _register(server: FastMCP) -> FastMCP:
    """Registra a MESMA superfície em qualquer instância (com ou sem auth)."""
    server.resource("lifeline://project/context")(project_context)
    server.tool()(lifeline_append)
    server.tool()(lifeline_recontextualize)
    server.tool()(lifeline_recall)
    server.custom_route("/healthz", methods=["GET"])(_healthz)
    server.custom_route("/oauth/consent", methods=["GET"])(_oauth_consent)  # Supabase OAuth Server
    return server


# instância default (local/stdio e testes) — sem auth
mcp = _register(FastMCP("Lifeline", instructions=_INSTRUCTIONS, icons=_ICONS, website_url=_WEBSITE))


# ---- OAuth Resource Server (multi-tenant) -------------------------------------------------

class SupabaseJWKSVerifier(TokenVerifier):
    """Valida o Bearer JWT do **OAuth Server nativo do Supabase** (decisão de trocar o AS
    hand-rolled pelo oficial) por **JWKS/ES256**, offline — sem chamar /auth/v1/user a cada
    request. Confere assinatura + issuer + expiração; o token ORIGINAL é mantido no AccessToken
    para escopar a RLS por usuário no PostgREST. Vale tanto p/ token do OAuth Server quanto p/
    token de sessão (mesma chave/issuer). `_jwk_client` injetável p/ teste."""

    def __init__(self, url: Optional[str] = None, jwks_uri: Optional[str] = None, _jwk_client=None,
                 audience: Optional[str] = None):
        from lifeline.cloud import clean_url
        self.url = clean_url(url or os.environ.get("SUPABASE_URL", ""))
        self.issuer = f"{self.url}/auth/v1"
        self.jwks_uri = jwks_uri or f"{self.issuer}/.well-known/jwks.json"
        self._jwk_client = _jwk_client
        # Opt-in audience pinning (S2): when LIFELINE_OAUTH_AUDIENCE is set we ALSO require the
        # token's `aud` to match — so a JWT minted for a different resource in the same Supabase
        # project is rejected here. Default stays OFF (issuer alone), to not break existing tokens
        # whose aud isn't fixed yet. Set it once you pin the OAuth Server's audience.
        self.audience = audience or os.environ.get("LIFELINE_OAUTH_AUDIENCE") or None

    def _client(self):
        if self._jwk_client is None:
            import jwt
            self._jwk_client = jwt.PyJWKClient(self.jwks_uri)  # busca+cacheia as chaves
        return self._jwk_client

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if not token:
            return None
        import jwt
        try:
            # PyJWKClient faz I/O bloqueante na 1ª vez (depois cacheia) → fora do event loop.
            signing_key = await asyncio.to_thread(self._client().get_signing_key_from_jwt, token)
            claims = jwt.decode(
                token, signing_key.key, algorithms=["ES256"], issuer=self.issuer,
                audience=self.audience,                       # None unless LIFELINE_OAUTH_AUDIENCE is set (S2)
                options={"verify_aud": bool(self.audience)},  # off by default — issuer guarantees the origin
            )
        except Exception:
            logging.getLogger("lifeline.mcp").info("JWKS verify falhou (token inválido/expirado)", exc_info=True)
            return None  # assinatura/issuer/exp inválidos → 401
        return AccessToken(token=token, client_id=claims.get("sub", "unknown"),
                           scopes=["lifeline"], expires_at=claims.get("exp"))


def _host_only(value: str) -> str:
    """Extrai só o host[:porta]. Tolera URL colada com https:// e barra final (erro comum no
    dashboard): ALLOWED_HOSTS precisa do host PURO — com esquema, o Host header não casa → 421."""
    value = value.strip().rstrip("/")
    if "://" in value:
        from urllib.parse import urlparse
        value = urlparse(value).netloc
    return value


def _transport_security() -> TransportSecuritySettings:
    """Atrás de túnel/proxy/deploy o Host header é o domínio público — o default localhost-only
    do FastMCP bloqueia com 421 'Invalid Host header'. `LIFELINE_MCP_ALLOWED_HOSTS=host1,host2`
    libera esses (proteção anti-DNS-rebinding ON); sem ele, desliga a proteção (o servidor remoto
    já é público de qualquer forma)."""
    hosts = os.environ.get("LIFELINE_MCP_ALLOWED_HOSTS", "").strip()
    if not hosts:
        hosts = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()  # Render injeta sozinho
    if hosts:
        allow = []
        for h in (x.strip() for x in hosts.split(",") if x.strip()):
            h = _host_only(h)   # tolera URL colada com https:// (erro comum) → host puro, senão 421
            if h:
                allow += [h, f"{h}:*"]
        return TransportSecuritySettings(allowed_hosts=allow)
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)


def _build_remote() -> FastMCP:
    """Servidor remoto. Três modos, por env (do mais completo ao mais simples):

      - LIFELINE_OAUTH_AS=1  → Authorization Server COMPLETO (open item #32d96c3d): DCR +
        authorization-code/PKCE + metadata, delegando login ao Supabase. É o que os
        conectores hospedados (claude.ai/ChatGPT/Gemini) exigem. Implica Resource Server.
      - LIFELINE_OAUTH=1     → Resource Server só (valida Bearer, multi-tenant via RLS). Útil
        quando um AS externo já emite os tokens.
      - (nenhum)            → sem auth (single-tenant via env).

    No deploy, `public`/host derivam de RENDER_EXTERNAL_URL/HOSTNAME automaticamente (menos
    config manual). E o MODO escolhido é ANUNCIADO no boot — com aviso ALTO se o AS/RS foi
    pedido mas não pôde ligar (env faltando), pra nunca mais cair em authless em silêncio."""
    ts = _transport_security()
    have_supa = (_STORE["kind"] == "supabase"
                 and os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"))
    port = int(os.environ.get("LIFELINE_MCP_PORT", "8000"))
    public = (os.environ.get("LIFELINE_MCP_PUBLIC_URL")
              or os.environ.get("RENDER_EXTERNAL_URL")        # Render injeta sozinho
              or f"http://localhost:{port}")
    want_as = os.environ.get("LIFELINE_OAUTH_AS") == "1"
    want_rs = os.environ.get("LIFELINE_OAUTH") == "1"

    # Anti-falha-calada: pediu auth e não dá pra ligar → DIGA exatamente o que falta (não some).
    if (want_as or want_rs) and not have_supa:
        miss = []
        if _STORE["kind"] != "supabase":
            miss.append("LIFELINE_STORE=supabase")
        if not os.environ.get("SUPABASE_URL"):
            miss.append("SUPABASE_URL")
        if not os.environ.get("SUPABASE_KEY"):
            miss.append("SUPABASE_KEY")
        print(f"[lifeline] WARNING: LIFELINE_OAUTH{'_AS' if want_as else ''}=1 requested, but "
              f"falling back to AUTHLESS — missing: {', '.join(miss)}", flush=True)

    if want_as and have_supa:
        from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
        from lifeline.oauth import SupabaseAuthServer, SupabaseClientStore
        # Login HOSPEDADO (sem ROPC) quando há provider social configurado; senão, form de senha (dev).
        login_provider = os.environ.get("LIFELINE_OAUTH_PROVIDER")
        # S3: the password form (ROPC) is a DEV-only path — it must not be silently exposed on a
        # public deploy. On a non-local public URL with no social provider, REFUSE unless explicitly
        # allowed, so production is hosted-login by default (a deliberate choice, never an accident).
        is_local = public.startswith(("http://localhost", "http://127.0.0.1", "http://0.0.0.0"))
        allow_pw = os.environ.get("LIFELINE_OAUTH_ALLOW_PASSWORD") == "1"
        if not login_provider and not is_local and not allow_pw:
            raise SystemExit(
                f"[lifeline] REFUSING to expose the dev-only password form (ROPC) on a public AS "
                f"deploy ({public}). Set LIFELINE_OAUTH_PROVIDER=github|google for hosted login "
                f"(recommended), or LIFELINE_OAUTH_ALLOW_PASSWORD=1 to override (NOT for production).")
        if not login_provider and not is_local:   # allowed by override → still say it out loud
            print("[lifeline] WARNING: exposing the dev-only password form (ROPC) on a public "
                  "deploy — LIFELINE_OAUTH_ALLOW_PASSWORD=1 is set. Prefer a social provider.", flush=True)
        # Persistência dos clients DCR: com a chave de serviço → tabela (sobrevive a restart/réplicas);
        # senão, em memória (instância única). É infra do AS, não dado de tenant (schema.sql:84-98).
        svc = os.environ.get("SUPABASE_SERVICE_ROLE")
        client_store = (SupabaseClientStore(url=os.environ["SUPABASE_URL"], service_key=svc)
                        if svc else None)
        provider = SupabaseAuthServer(
            supabase_url=os.environ["SUPABASE_URL"], supabase_key=os.environ["SUPABASE_KEY"],
            public_url=public, login_provider=login_provider, client_store=client_store)
        server = _register(FastMCP(
            "Lifeline", instructions=_INSTRUCTIONS, icons=_ICONS, website_url=_WEBSITE,
            auth_server_provider=provider,            # provê DCR/authorize/token/metadata + introspecção
            auth=AuthSettings(issuer_url=public, resource_server_url=public, required_scopes=[],
                              client_registration_options=ClientRegistrationOptions(enabled=True)),
            transport_security=ts))
        provider.register_login_routes(server)        # /oauth/login + /oauth/callback (delega ao Supabase)
        login_mode = (f"HOSTED via {login_provider}" if login_provider else "password form (dev)")
        store_mode = "persistent (lifeline_oauth_clients)" if svc else "in-memory"
        print(f"[lifeline] mode: AUTHORIZATION SERVER (DCR + auth-code/PKCE) · login={login_mode} "
              f"· clients={store_mode} · public={public}", flush=True)
        return server

    if want_rs and have_supa:
        from mcp.server.auth.settings import AuthSettings
        from lifeline.cloud import clean_url
        # O AS é o OAuth Server NATIVO do Supabase (#0049 superseou o AS próprio): a metadata
        # de protected-resource aponta o claude.ai pra cá; ele descobre /.well-known/oauth-
        # authorization-server/auth/v1 (RFC 8414 com path), faz DCR/authorize/token DIRETO no
        # Supabase, e o login hospedado (inclui Google/GitHub) é deles. Validamos por JWKS.
        issuer = os.environ.get("LIFELINE_OAUTH_ISSUER",
                                f"{clean_url(os.environ['SUPABASE_URL'])}/auth/v1")
        print(f"[lifeline] mode: RESOURCE SERVER (AS = Supabase OAuth Server, JWKS) · "
              f"issuer={issuer} · public={public}", flush=True)
        return _register(FastMCP(
            "Lifeline", instructions=_INSTRUCTIONS, icons=_ICONS, website_url=_WEBSITE,
            token_verifier=SupabaseJWKSVerifier(),
            auth=AuthSettings(issuer_url=issuer, resource_server_url=public, required_scopes=[]),
            transport_security=ts,
        ))
    print(f"[lifeline] mode: AUTHLESS (single-tenant) · public={public}", flush=True)
    return _register(FastMCP("Lifeline", instructions=_INSTRUCTIONS, icons=_ICONS, website_url=_WEBSITE,
                             transport_security=ts))


def main():
    """Entry point (`lifeline-mcp`) — serve via stdio (local)."""
    _configure()
    mcp.run()


def main_remote():
    """Entry point (`lifeline-mcp-remote`) — serve por HTTP/SSE (superfície remota).

    Bind via LIFELINE_MCP_HOST/PORT (default 0.0.0.0:8000); transporte
    LIFELINE_MCP_TRANSPORT ('sse' default ou 'streamable-http'). LIFELINE_OAUTH=1 liga o
    Resource Server (Bearer obrigatório, multi-tenant). Escrita continua HITL.
    """
    _configure()
    server = _build_remote()
    server.settings.host = os.environ.get("LIFELINE_MCP_HOST", "0.0.0.0")
    server.settings.port = int(os.environ.get("LIFELINE_MCP_PORT", "8000"))
    server.run(transport=os.environ.get("LIFELINE_MCP_TRANSPORT", "sse"))


if __name__ == "__main__":
    main()
