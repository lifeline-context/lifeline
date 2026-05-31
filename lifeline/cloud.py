"""Adapter Supabase (M3 Tier 1) — implementa o port `EventStore` sobre o PostgREST do
Supabase. Promovido ao pacote: importável após install e coberto por testes.

Disciplina (segue #0039): os testes de transporte MOCKADOS provam o *wire* (que requests
saem certas e que parseamos as respostas). O CONTRATO real (schema/RLS/PostgREST) só é
provado pelo teste live skip-gated em tests/test_supabase.py, que roda quando
SUPABASE_URL/KEY estão no ambiente. Enquanto esse teste não passa contra um projeto,
trate como "wired, não validado ao vivo".

Auth (importante — o teste live vai cobrar isso): o schema usa `owner default auth.uid()`
e RLS `owner = auth.uid()`. Logo o SUPABASE_KEY deve ser um ACCESS TOKEN DE USUÁRIO (JWT)
para `auth.uid()` resolver e o INSERT passar na RLS. A service_role bypassa a RLS mas
deixa `owner` nulo — não serve para escrita multi-tenant. NUNCA comite a key.

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
                 key: Optional[str] = None, transport: Any = None):
        url = url or os.environ.get("SUPABASE_URL")
        key = key or os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "defina SUPABASE_URL e SUPABASE_KEY (use um .env; NUNCA comite a key). "
                "SUPABASE_KEY deve ser um access token de usuário para a RLS resolver auth.uid()."
            )
        self.line = line
        self.url = url.rstrip("/")
        self.key = key
        self.base = f"{self.url}/rest/v1/{TABLE}"
        self._transport = transport  # None = real; httpx.MockTransport(...) nos testes

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=30, transport=self._transport)

    def _headers(self, extra=None):
        h = {"apikey": self.key, "Authorization": f"Bearer {self.key}",
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
