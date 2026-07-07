"""Prova o `lifeline rehash`: migra um ledger escrito sob o canônico ANTIGO (v1, colidível)
para o atual (v2, injetivo), remapeando parents old→new em ordem topológica — mesma verdade
(contagem, supersessão, bodies), ids novos, verify OK no fim. Recusa dano estrutural."""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry                 # noqa: E402
from lifeline.store import SQLiteEventStore      # noqa: E402
from lifeline.state import StateEngine           # noqa: E402
from lifeline import cli                          # noqa: E402


def _old_canonical(self):
    """O esquema v1 (join por \\n, não-injetivo) — como os ledgers pré-0.5.0 foram selados."""
    fields = [self.kind, self.author, self.agent, self.provider,
              self.model, self.summary, self.body.strip()]
    return "\n".join(fields) + "\n" + "|".join(sorted(self.parents)) + "\n"


def _e(summary, body="why", kind="decision", parents=None):
    return Entry(author="a", agent="x", provider="p", model="m",
                 kind=kind, summary=summary, body=body, parents=parents or [])


class TestRehash(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = os.path.join(self.dir, ".lifeline", "ledger.db")
        self.out = os.path.join(self.dir, "LIFELINE.md")
        os.makedirs(os.path.dirname(self.db))

    async def asyncTearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    async def _build_v1_ledger(self):
        """Ledger selado sob o canônico v1: root → decisão → decisão → correção(supersede) → merge."""
        store = SQLiteEventStore(self.db)
        await store.initialize()
        with mock.patch.object(Entry, "_canonical", _old_canonical):
            e1 = _e("founds the project", kind="bootstrap")
            await store.append(e1)
            e2 = _e("decision A (will be reverted)", parents=[e1.id])
            await store.append(e2)
            e3 = _e("decision B (stays)", parents=[e2.id])
            await store.append(e3)
            c4 = _e("revert A", kind="correction", parents=[e2.id])
            await store.append(c4)
            e5 = _e("merge point", kind="note", parents=[e3.id, c4.id])
            await store.append(e5)
        return [e1, e2, e3, c4, e5]

    async def test_rehash_migrates_v1_ledger_to_verify_ok(self):
        olds = await self._build_v1_ledger()
        # pré-condição do cenário real: sob o código NOVO, o ledger v1 está todo "tampered"
        ok, n, tampered, dangling = await cli.cmd_verify(self.db)
        self.assertFalse(ok)
        self.assertEqual(len(tampered), 5)
        self.assertEqual(dangling, [])

        changed, total, _ = await cli.cmd_rehash(self.db, self.out)
        self.assertEqual((changed, total), (5, 5))       # todos os ids migraram

        ok2, n2, t2, d2 = await cli.cmd_verify(self.db)  # e agora a cadeia verifica
        self.assertTrue(ok2)
        self.assertEqual(n2, 5)
        self.assertTrue(os.path.exists(self.db + ".bak"))   # rollback disponível

        # a VERDADE é a mesma: decisão A segue supersedida, B segue em vigor
        st = await StateEngine(SQLiteEventStore(self.db)).reduce()
        in_force = {d["summary"] for d in st.get("decisions", [])}
        self.assertIn("decision B (stays)", in_force)
        self.assertNotIn("decision A (will be reverted)", in_force)
        # e nenhum id antigo sobreviveu (remap completo, inclusive nos parents do merge)
        news = {e.id async for e in SQLiteEventStore(self.db).stream()}
        self.assertTrue(news.isdisjoint({o.id for o in olds}))

    async def test_rehash_round_trips_through_the_regenerated_view(self):
        await self._build_v1_ledger()
        await cli.cmd_rehash(self.db, self.out)
        # a view regenerada re-ingere para os MESMOS ids (strict passa — nada de mismatch)
        from lifeline.ingest import ingest_markdown
        fresh = SQLiteEventStore(os.path.join(self.dir, "fresh.db"))
        await fresh.initialize()
        n = await ingest_markdown(self.out, fresh, strict=True)
        self.assertEqual(n, 5)
        a = sorted([e.id async for e in SQLiteEventStore(self.db).stream()])
        b = sorted([e.id async for e in fresh.stream()])
        self.assertEqual(a, b)

    async def test_rehash_is_idempotent(self):
        await self._build_v1_ledger()
        await cli.cmd_rehash(self.db, self.out)
        changed2, total2, _ = await cli.cmd_rehash(self.db, self.out)   # segunda passada
        self.assertEqual((changed2, total2), (0, 5))                     # nada muda

    async def test_rehash_refuses_structural_damage(self):
        await self._build_v1_ledger()
        con = sqlite3.connect(self.db)                    # simula OMISSÃO: some com o meio
        con.execute("DELETE FROM entries WHERE seq=2")
        con.commit()
        con.close()
        with self.assertRaises(ValueError):
            await cli.cmd_rehash(self.db, self.out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
