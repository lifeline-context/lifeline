"""Prova o grafo tipado (Fase 1 do Regente, ainda MEMÓRIA): relações como entries
(parents=[from,to], direção no body porque parents é set no hash), projeção em vigor
(supersedidas somem), consulta estruturada, e round-trip/verify intactos (sem rehash)."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry                         # noqa: E402
from lifeline.store import SQLiteEventStore              # noqa: E402
from lifeline.graph import ProjectGraph, parse_relation  # noqa: E402
from lifeline import cli                                  # noqa: E402


def _e(kind, summary, body="", parents=None):
    return Entry(author="a", agent="x", provider="p", model="m",
                 kind=kind, summary=summary, body=body, parents=parents or [])


class TestProjectGraph(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = os.path.join(self.dir, "g.db")
        self.store = SQLiteEventStore(self.db)
        await self.store.initialize()
        self.api = _e("api", "UserService API")
        await self.store.append(self.api)
        self.svc = _e("service", "AuthService")
        await self.store.append(self.svc)
        self.tst = _e("test", "auth integration tests")
        await self.store.append(self.tst)

    async def asyncTearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    async def _relate(self, rel, a, b):
        e, ins, _ = await cli.cmd_relate(self.db, os.path.join(self.dir, "V.md"), rel, a.id, b.id, "me")
        return e

    async def test_depends_on_is_directional_and_structured(self):
        await self._relate("depends_on", self.svc, self.api)     # AuthService depends_on UserService API
        g = await ProjectGraph.build(self.store)
        # "do que o AuthService depende?" → a API (saída)
        out = g.outgoing(self.svc.id, "depends_on")
        self.assertEqual([h["id"] for h in out], [self.api.id])
        self.assertEqual(out[0]["kind"], "api")
        # "quem depende da API?" → o AuthService (entrada) — direção preservada
        inc = g.incoming(self.api.id, "depends_on")
        self.assertEqual([h["id"] for h in inc], [self.svc.id])
        # a API NÃO depende do AuthService (não é simétrico)
        self.assertEqual(g.outgoing(self.api.id, "depends_on"), [])

    async def test_direction_survives_even_though_parents_is_a_set(self):
        # o hash ordena os parents → a ordem se perde; a direção tem de vir do body
        r = await self._relate("depends_on", self.svc, self.api)
        parsed = parse_relation(r.body)
        self.assertEqual(parsed["from"], self.svc.id)
        self.assertEqual(parsed["to"], self.api.id)
        self.assertEqual(sorted(r.parents), sorted([self.svc.id, self.api.id]))  # set no hash

    async def test_superseded_relation_drops_from_the_graph(self):
        r = await self._relate("depends_on", self.svc, self.api)
        g1 = await ProjectGraph.build(self.store)
        self.assertEqual(len(g1.edges), 1)
        # reverte a relação com uma correction que a supersede
        await self.store.append(_e("correction", "drop that dependency", "why", parents=[r.id]))
        g2 = await ProjectGraph.build(self.store)
        self.assertEqual(g2.edges, [])                           # sumiu da verdade atual

    async def test_relation_is_content_addressed_no_rehash(self):
        # relação nova NÃO muda ids existentes nem quebra o verify (aditivo, Fase 1)
        before = {e.id async for e in self.store.stream()}
        await self._relate("tests_covers", self.tst, self.svc)
        ok, n, tampered, dangling = await cli.cmd_verify(self.db)
        self.assertTrue(ok)                                       # cadeia intacta
        self.assertEqual(tampered, [])
        after = {e.id async for e in self.store.stream()}
        self.assertTrue(before.issubset(after))                  # nada recomputou

    async def test_cmd_graph_dependents_answers_structurally(self):
        await self._relate("depends_on", self.svc, self.api)
        await self._relate("depends_on", self.tst, self.api)     # dois dependentes da API
        full, node, verb, hits = await cli.cmd_graph(self.db, dependents=self.api.id[:8])
        self.assertEqual(node["kind"], "api")
        self.assertEqual(sorted(h["id"] for h in hits), sorted([self.svc.id, self.tst.id]))

    async def test_relate_rejects_unknown_relation_and_orphan(self):
        from lifeline.graph import relation_body
        with self.assertRaises(ValueError):
            relation_body("owns", self.svc.id, self.api.id)      # relação inexistente
        with self.assertRaises(ValueError):                       # ponta órfã (prefixo sem match)
            await cli.cmd_relate(self.db, os.path.join(self.dir, "V.md"),
                                 "depends_on", "deadbeef00", self.api.id, "me")


if __name__ == "__main__":
    unittest.main(verbosity=2)
