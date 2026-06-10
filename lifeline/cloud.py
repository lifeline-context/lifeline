"""Adapters Supabase (M3 Tier 1) — `SupabaseEventStore` (ledger) e `SupabaseStagingStore`
(fila HITL) sobre o PostgREST do Supabase. Implementam os ports `EventStore`/`StagingStore`,
então o resto do Lifeline funciona igual, só trocando o backend.

Disciplina (#0039): os testes de transporte MOCKADOS provam o *wire*; o CONTRATO real
(schema/RLS/PostgREST) é provado pelo teste live skip-gated em tests/test_supabase.py.

Resiliência (#0050): toda resposta passa por `_ensure_ok` → 4xx/5xx é LOGADO e LEVANTA
(httpx.HTTPStatusError). NUNCA mascaramos falha como sucesso/dedup — o `append` distingue
inserção (linha retornada → True) de duplicata ignorada ([] → False), igual ao SQLite.

Auth (VALIDADO ao vivo, #0042): o gateway exige DOIS valores — CHAVE DO PROJETO no header
`apikey` (anon/publishable) e o token no `Authorization: Bearer`. Logo:
  - SUPABASE_KEY   = apikey do projeto (anon p/ leitura; a RLS isola por tenant);
  - SUPABASE_TOKEN = access token de usuário (JWT) p/ ESCRITA — só aí `auth.uid()` resolve.
NUNCA comite chave nem token. Pré-requisito: rodar cloud/schema.sql no projeto.
"""
import json
import logging
import os
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from lifeline.entry import Entry
from lifeline.staging import StagingStore
from lifeline.store import EventStore

TABLE = "lifeline_entries"
PROPOSALS = "lifeline_proposals"
_log = logging.getLogger("lifeline.cloud")


def clean_url(url: str) -> str:
    """Normaliza a URL do Supabase na ENTRADA: tira espaços/quebras, garante o esquema
    https:// e remove a barra final. Colar a URL SEM `https://` no dashboard é o erro mais
    comum — e sem esquema o httpx levanta UnsupportedProtocol, que virava um 500 cru no
    fluxo de auth. Consertar aqui mata a classe inteira do problema."""
    url = (url or "").strip()
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def _ensure_ok(r: httpx.Response) -> httpx.Response:
    """4xx/5xx → loga (status + trecho do corpo) e levanta. Falha de rede nunca vira
    sucesso silencioso. Não loga headers/token."""
    if r.is_error:
        _log.error("Supabase %s %s -> %s: %s", r.request.method, r.request.url,
                   r.status_code, (r.text or "")[:200])
        r.raise_for_status()
    return r


class _SupabaseBase:
    """Resolução de credenciais + cliente httpx + headers, compartilhados pelos adapters.
    `transport` é injetável para teste (httpx.MockTransport)."""

    def __init__(self, table: str, line: str = "ledger", url: Optional[str] = None,
                 key: Optional[str] = None, token: Optional[str] = None, transport: Any = None):
        explicit_key = key is not None      # construção explícita (ex.: testes) não herda env
        url = url or os.environ.get("SUPABASE_URL")
        key = key or os.environ.get("SUPABASE_KEY")
        if token is None and not explicit_key:
            token = os.environ.get("SUPABASE_TOKEN")
        token = token or key
        if not url or not key:
            raise ValueError(
                "defina SUPABASE_URL e SUPABASE_KEY (apikey do projeto = anon/publishable; "
                "use um .env, NUNCA comite). Para ESCRITA autenticada sob RLS defina também "
                "SUPABASE_TOKEN = access token de usuário (JWT): o gateway exige o apikey do "
                "projeto no header `apikey` e o JWT no `Authorization: Bearer` (dois valores)."
            )
        self.line = line
        self.url = clean_url(url)
        self.key = key.strip()
        self.token = (token or "").strip()
        self.base = f"{self.url}/rest/v1/{table}"
        self._transport = transport  # None = real; httpx.MockTransport(...) nos testes

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=30, transport=self._transport)

    def _headers(self, extra=None):
        # apikey = chave do projeto (gateway); Bearer = token do usuário (RLS/auth.uid()).
        h = {"apikey": self.key, "Authorization": f"Bearer {self.token}",
             "Content-Type": "application/json"}
        if extra:
            h.update(extra)
        return h


class SupabaseEventStore(_SupabaseBase, EventStore):
    """Ledger remoto via PostgREST (append-only; a RLS nega UPDATE/DELETE)."""

    def __init__(self, line: str = "ledger", url=None, key=None, token=None, transport: Any = None):
        super().__init__(TABLE, line, url, key, token, transport)

    @staticmethod
    def _to_entry(payload) -> Entry:
        # payload vem como objeto JSON (dict); model_validate_json espera string ISO p/ datetime.
        return Entry.model_validate_json(json.dumps(payload))

    async def initialize(self) -> None:
        pass  # schema é criado uma vez via cloud/schema.sql

    async def append(self, entry: Entry) -> bool:
        row = {
            "line": self.line, "id": entry.id, "ts": entry.ts.isoformat(), "kind": entry.kind,
            "summary": entry.summary, "body": entry.body, "parents": entry.parents,
            "dedup_key": entry.dedup_key, "payload": json.loads(entry.model_dump_json()),
        }
        async with self._client() as c:
            r = await c.post(self.base, json=row, headers=self._headers(
                {"Prefer": "resolution=ignore-duplicates,return=representation"}))
        _ensure_ok(r)  # 4xx/5xx → log + raise (não mascara falha como dedup)
        # representation: linha retornada = inserida; [] = duplicata ignorada (igual ao SQLite).
        return bool(r.json())

    async def get(self, entry_id: str) -> Optional[Entry]:
        async with self._client() as c:
            r = await c.get(self.base, headers=self._headers(), params={
                "line": f"eq.{self.line}", "id": f"eq.{entry_id}", "select": "payload"})
        rows = _ensure_ok(r).json()
        return self._to_entry(rows[0]["payload"]) if rows else None

    def stream(self) -> AsyncIterator[Entry]:
        async def _gen():
            async with self._client() as c:
                r = await c.get(self.base, headers=self._headers(), params={
                    "line": f"eq.{self.line}", "select": "payload", "order": "seq.asc"})
            for row in _ensure_ok(r).json():
                yield self._to_entry(row["payload"])
        return _gen()

    async def parents(self, entry_id: str) -> List[Entry]:
        e = await self.get(entry_id)
        out = []
        for pid in (e.parents if e else []):
            p = await self.get(pid)
            if p:
                out.append(p)
        return out

    async def children(self, entry_id: str) -> List[Entry]:
        async with self._client() as c:
            r = await c.get(self.base, headers=self._headers(), params={
                "line": f"eq.{self.line}", "parents": f'cs.["{entry_id}"]',
                "select": "payload", "order": "seq.asc"})
        return [self._to_entry(row["payload"]) for row in _ensure_ok(r).json()]


class SupabaseStagingStore(_SupabaseBase, StagingStore):
    """Fila HITL remota via PostgREST. MUTÁVEL (status muda) — a RLS permite UPDATE, não DELETE."""

    def __init__(self, line: str = "ledger", url=None, key=None, token=None, transport: Any = None):
        super().__init__(PROPOSALS, line, url, key, token, transport)

    @staticmethod
    def _norm(row: Dict) -> Dict:
        # `parents` vem como lista (jsonb); o consumidor (cmd_approve) espera string JSON,
        # igual ao adapter SQLite. Normaliza para manter o fluxo agnóstico de backend.
        row = dict(row)
        row["parents"] = json.dumps(row.get("parents") or [])
        return row

    async def initialize(self) -> None:
        pass  # tabela lifeline_proposals criada via cloud/schema.sql

    async def propose(self, *, kind, summary, body, author, agent, provider, model, parents=None) -> int:
        row = {"line": self.line, "kind": kind, "summary": summary, "body": body or "",
               "author": author, "agent": agent, "provider": provider, "model": model,
               "parents": parents or []}
        async with self._client() as c:
            r = await c.post(self.base, json=row, headers=self._headers({"Prefer": "return=representation"}))
        return _ensure_ok(r).json()[0]["pid"]

    async def pending(self) -> List[Dict]:
        async with self._client() as c:
            r = await c.get(self.base, headers=self._headers(), params={
                "line": f"eq.{self.line}", "status": "eq.pending", "order": "pid.asc", "select": "*"})
        return [self._norm(row) for row in _ensure_ok(r).json()]

    async def get(self, pid: int) -> Optional[Dict]:
        async with self._client() as c:
            r = await c.get(self.base, headers=self._headers(), params={
                "pid": f"eq.{pid}", "select": "*"})
        rows = _ensure_ok(r).json()
        return self._norm(rows[0]) if rows else None

    async def set_status(self, pid: int, status: str) -> None:
        async with self._client() as c:
            r = await c.patch(self.base, params={"pid": f"eq.{pid}"},
                              json={"status": status}, headers=self._headers())
        _ensure_ok(r)
