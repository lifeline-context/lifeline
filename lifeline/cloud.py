"""Adapter Supabase (M3 Tier 1) — implementa o port `EventStore` sobre o PostgREST do
Supabase. Promovido ao pacote: importável após install e coberto por testes.

Disciplina (segue #0039): os testes de transporte MOCKADOS provam o *wire* (que requests
saem certas e que parseamos as respostas). O CONTRATO real (schema/RLS/PostgREST) só é
provado pelo teste live skip-gated em tests/test_supabase.py, que roda quando
SUPABASE_URL/KEY estão no ambiente. Enquanto esse teste não passa contra um projeto,
trate como "wired, não validado ao vivo".

Auth (VALIDADO ao vivo, 2026-05-31): o gateway do Supabase exige DOIS valores distintos —
a CHAVE DO PROJETO no header `apikey` (anon/publishable) e o token no `Authorization:
Bearer`. Usar o JWT de usuário como `apikey` dá 401 "Invalid API key". Logo:
  - SUPABASE_KEY   = apikey do projeto (anon p/ leitura; a RLS isola por tenant);
  - SUPABASE_TOKEN = access token de usuário (JWT) p/ ESCRITA — só aí `auth.uid()` resolve,
    `owner` é setado e o INSERT passa a RLS. Se ausente, cai no próprio apikey (serve p/
    service_role ou leitura anon). NUNCA comite chave nem token.

Pré-requisito: rodar cloud/schema.sql no projeto (SQL Editor ou via MCP).
"""
import json
import os
from typing import Any, AsyncIterator, List, Optional

import httpx

from lifeline.entry import Entry
from lifeline.store import EventStore

TABLE = "lifeline_entries"


class SupabaseEventStore(EventStore):
    """EventStore remoto via PostgREST. `transport` é injetável para teste (httpx.MockTransport)."""

    def __init__(self, line: str = "ledger", url: Optional[str] = None,
                 key: Optional[str] = None, token: Optional[str] = None, transport: Any = None):
        explicit_key = key is not None      # construção explícita (ex.: testes) não herda env
        url = url or os.environ.get("SUPABASE_URL")
        key = key or os.environ.get("SUPABASE_KEY")
        # Token de autorização (Bearer): JWT de usuário p/ a RLS resolver auth.uid() na ESCRITA.
        # Só consulta o ambiente quando a key NÃO veio explícita (senão herdaria token alheio nos
        # testes). Fallback final = o próprio apikey (serve p/ service_role ou leitura anon).
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
        self.url = url.rstrip("/")
        self.key = key
        self.token = token
        self.base = f"{self.url}/rest/v1/{TABLE}"
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
                {"Prefer": "resolution=ignore-duplicates,return=minimal"}))
        # 201 inserido; 200/204 quando duplicado foi ignorado → idempotência (content-addressed).
        return r.status_code in (200, 201, 204)

    async def get(self, entry_id: str) -> Optional[Entry]:
        async with self._client() as c:
            r = await c.get(self.base, headers=self._headers(), params={
                "line": f"eq.{self.line}", "id": f"eq.{entry_id}", "select": "payload"})
        rows = r.json()
        return self._to_entry(rows[0]["payload"]) if rows else None

    def stream(self) -> AsyncIterator[Entry]:
        async def _gen():
            async with self._client() as c:
                r = await c.get(self.base, headers=self._headers(), params={
                    "line": f"eq.{self.line}", "select": "payload", "order": "seq.asc"})
            for row in r.json():
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
        return [self._to_entry(row["payload"]) for row in r.json()]
