"""Prova a gerência de LINES (bugs L1–L4 da auditoria + o promote L5):
L1 LIFELINE_LINE vale no MCP local (antes era no-op fora da nuvem);
L2 staging da nuvem é escopado por line em get/set_status (antes vazava cross-line);
L3 clone reconstrói TODAS as lines (antes só a default);
L4 `lines` funciona na nuvem;
L5 promote copia entre lines como root, idempotente por content-addressing."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx                                              # noqa: E402
import lifeline.mcp_server as srv                          # noqa: E402
from lifeline import cli                                   # noqa: E402
from lifeline.cli import (                                 # noqa: E402
    cmd_clone, cmd_log, cmd_promote, cmd_push, cmd_verify, resolve_paths)
from lifeline.cloud import SupabaseEventStore, SupabaseStagingStore  # noqa: E402
from lifeline.store import SQLiteEventStore                # noqa: E402


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


class TestL1LocalMcpLine(unittest.TestCase):
    """LIFELINE_LINE tem de valer no modo LOCAL: o db do servidor deriva da line."""

    def setUp(self):
        self.addCleanup(lambda: cli._STORE.update(kind="sqlite", line="ledger"))
        self._db = srv._DB
        self.addCleanup(setattr, srv, "_DB", self._db)

    def test_line_env_derives_local_db(self):
        with mock.patch.dict(os.environ, {"LIFELINE_LINE": "research"}, clear=True):
            srv._configure()
        self.assertEqual(srv._DB, os.path.join(".lifeline", "research.db"))

    def test_explicit_db_wins_over_line(self):
        env = {"LIFELINE_LINE": "research", "LIFELINE_DB": os.path.join("x", "custom.db")}
        with mock.patch.dict(os.environ, env, clear=True):
            srv._configure()
        self.assertEqual(srv._DB, os.path.join("x", "custom.db"))

    def test_default_stays_ledger(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            srv._configure()
        self.assertEqual(srv._DB, os.path.join(".lifeline", "ledger.db"))


class TestL2CloudStagingLineScope(unittest.IsolatedAsyncioTestCase):
    """get/set_status na nuvem levam o filtro de line no wire — e por isso não cruzam lines."""

    def _store(self, line, handler):
        return SupabaseStagingStore(line=line, url="https://p.supabase.co", key="anon",
                                    transport=httpx.MockTransport(handler))

    async def test_get_is_line_scoped(self):
        seen = []
        rows = [{"pid": 7, "line": "research", "status": "pending", "kind": "note",
                 "summary": "s", "body": "b", "parents": []}]

        def handler(req):
            seen.append(req)
            # PostgREST real: o filtro line=eq.X restringe as linhas devolvidas
            want = req.url.params.get("line", "")
            return httpx.Response(200, json=[r for r in rows
                                             if want == f"eq.{r['line']}"])
        self.assertIsNotNone(await self._store("research", handler).get(7))   # mesma line → acha
        self.assertIsNone(await self._store("ledger", handler).get(7))        # outra line → None
        for req in seen:
            self.assertIn("line", req.url.params)                             # filtro SEMPRE no wire

    async def test_set_status_is_line_scoped(self):
        seen = []

        def handler(req):
            seen.append(req)
            return httpx.Response(204)
        await self._store("research", handler).set_status(7, "approved")
        self.assertEqual(seen[0].url.params.get("line"), "eq.research")


class TestL4CloudLines(unittest.IsolatedAsyncioTestCase):
    async def test_lines_lists_and_counts_cloud_lines(self):
        def handler(req):
            return httpx.Response(200, json=[{"line": "ledger"}, {"line": "ledger"},
                                             {"line": "strategy"}])
        s = SupabaseEventStore(line="ledger", url="https://p.supabase.co", key="anon",
                               transport=httpx.MockTransport(handler))
        self.assertEqual(await s.lines(), [("ledger", 2), ("strategy", 1)])

    def test_lines_cli_no_longer_local_only(self):
        self.assertNotIn("lines", cli._LOCAL_ONLY)


class TestL3CloneAllLines(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.root = tempfile.mkdtemp()
        self.bare = os.path.join(self.root, "remote.git")
        _git(["init", "--bare", "-b", "main", self.bare], self.root)
        self.A = os.path.join(self.root, "A")
        os.makedirs(self.A)
        _git(["init", "-b", "main"], self.A)
        _git(["config", "user.email", "t@t"], self.A)
        _git(["config", "user.name", "t"], self.A)
        _git(["remote", "add", "origin", self.bare], self.A)
        self.prev = os.getcwd()

    async def asyncTearDown(self):
        os.chdir(self.prev)
        shutil.rmtree(self.root, ignore_errors=True)

    async def test_clone_rebuilds_every_line(self):
        os.chdir(self.A)
        # duas lines no projeto A: a default e uma nomeada
        await cmd_log(os.path.join(".lifeline", "ledger.db"), "LIFELINE.md",
                      "decision", "main-line decision", "why", "me", "x", "p", "m", None)
        db2, out2 = resolve_paths("businessplan", None, None)
        await cmd_log(db2, out2, "decision", "pricing decision", "why $", "me", "x", "p", "m", None)
        ok, msg = await cmd_push(os.path.join(".lifeline", "ledger.db"), "LIFELINE.md")
        self.assertTrue(ok, msg)
        os.chdir(self.prev)

        B = os.path.join(self.root, "B")
        ok2, msg2 = await cmd_clone(self.bare, B)
        self.assertTrue(ok2, msg2)
        self.assertIn("2 line(s)", msg2)                       # ambas reconstruídas + verificadas
        for db, expected in [(os.path.join(B, ".lifeline", "ledger.db"), "main-line decision"),
                             (os.path.join(B, ".lifeline", "businessplan.db"), "pricing decision")]:
            store = SQLiteEventStore(db)
            await store.initialize()
            self.assertIn(expected, [e.summary async for e in store.stream()])


class TestL5Promote(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()
        self.prev = os.getcwd()
        os.chdir(self.dir)                                     # promote resolve paths por line

    async def asyncTearDown(self):
        os.chdir(self.prev)
        shutil.rmtree(self.dir, ignore_errors=True)

    async def _seed(self, line, summary, kind="decision", body="the why"):
        db, out = cli._line_paths(line)
        e, _, _ = await cmd_log(db, out, kind, summary, body, "me", "x", "p", "m", None)
        return e

    async def test_promote_copies_as_root_with_provenance(self):
        e = await self._seed("research", "winning approach")
        promoted, dups, _ = await cmd_promote("research", "ledger", ids=[e.id[:8]])  # prefixo ok
        self.assertEqual((len(promoted), dups), (1, 0))
        self.assertEqual(promoted[0].parents, [])              # ROOT no destino
        self.assertIn("promoted from research#", promoted[0].body)
        db, _ = cli._line_paths("ledger")
        ok, n, _, _ = await cmd_verify(db)                     # destino íntegro
        self.assertTrue(ok)

    async def test_promote_is_idempotent(self):
        e = await self._seed("research", "winning approach")
        await cmd_promote("research", "ledger", ids=[e.id])
        promoted2, dups2, _ = await cmd_promote("research", "ledger", ids=[e.id])
        self.assertEqual((len(promoted2), dups2), (0, 1))      # re-promover = no-op (dedup)

    async def test_promote_by_kind_skips_superseded(self):
        a = await self._seed("research", "decision kept")
        b = await self._seed("research", "decision reverted")
        db, out = cli._line_paths("research")
        await cmd_log(db, out, "correction", "revert it", "why", "me", "x", "p", "m", [b.id])
        promoted, _, _ = await cmd_promote("research", "ledger", kind="decision")
        self.assertEqual([p.summary for p in promoted], ["decision kept"])   # morta não vai

    async def test_promote_refuses_corrections_and_same_line(self):
        await self._seed("research", "root", kind="bootstrap")
        db, out = cli._line_paths("research")
        e, _, _ = await cmd_log(db, out, "correction", "a correction", "why",
                                "me", "x", "p", "m", None)
        with self.assertRaises(ValueError):
            await cmd_promote("research", "ledger", ids=[e.id])
        with self.assertRaises(ValueError):
            await cmd_promote("research", "research", ids=[e.id])


if __name__ == "__main__":
    unittest.main(verbosity=2)
