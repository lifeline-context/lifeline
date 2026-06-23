"""Prova as garantias de corrida do content-addressing (Lei #3): idempotência sob appends
concorrentes (mesma corrida → 1 entrada) e merge de views divergentes (união sem duplicatas,
integridade intacta). Sem isso, a promessa "mesmo conteúdo → mesmo id em qualquer máquina"
ficava só afirmada, não provada."""
import asyncio
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry                         # noqa: E402
from lifeline.store import SQLiteEventStore              # noqa: E402
from lifeline.state import StateEngine                   # noqa: E402
from lifeline.projection import render_ledger_markdown   # noqa: E402
from lifeline.ingest import ingest_text                  # noqa: E402


def _e(summary, body, kind="decision", parents=None):
    return Entry(author="a", agent="x", provider="p", model="m",
                 kind=kind, summary=summary, body=body, parents=parents or [])


class TestConcurrencyAndMerge(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()

    async def asyncTearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    async def _store(self, name):
        s = SQLiteEventStore(os.path.join(self.dir, name))
        await s.initialize()
        return s

    async def test_concurrent_identical_appends_dedup_to_one(self):
        # N Entry objects with IDENTICAL content → one content-addressed id (ts/dedup_key are
        # OUTSIDE the hash, Law #3). Appended concurrently, exactly one insert may win.
        store = await self._store("race.db")
        entries = [_e("same decision", "same why") for _ in range(16)]
        self.assertEqual(len({e.id for e in entries}), 1)        # all share one id (content-addressed)

        results = await asyncio.gather(*(store.append(e) for e in entries))
        self.assertEqual(sum(1 for r in results if r), 1)        # exactly one append won the race
        rows = [e async for e in store.stream()]
        self.assertEqual(len(rows), 1)                           # store holds exactly one entry

    async def test_divergent_views_merge_is_union_without_dupes(self):
        # Two collaborators fork from a shared prefix, each adding a different entry. Merging both
        # markdown views into one store must dedup the shared entries (same id) and keep both
        # divergences — a union, not a duplication — with integrity intact.
        view_a = await self._store("a.db")
        e0 = _e("project root", "why root", kind="bootstrap")
        await view_a.append(e0)
        e1 = _e("shared decision", "why shared", parents=[e0.id])
        await view_a.append(e1)
        eA = _e("A-only branch", "why A", parents=[e1.id])
        await view_a.append(eA)

        view_b = await self._store("b.db")
        for e in (e0, e1):
            await view_b.append(e)                               # same shared prefix (same ids)
        eB = _e("B-only branch", "why B", parents=[e1.id])
        await view_b.append(eB)

        md_a = await render_ledger_markdown(view_a)
        md_b = await render_ledger_markdown(view_b)

        merged = await self._store("merged.db")
        n_a = await ingest_text(md_a, merged)
        n_b = await ingest_text(md_b, merged)
        self.assertEqual(n_a, 3)                                 # e0, e1, eA all new
        self.assertEqual(n_b, 1)                                 # e0/e1 deduped → only eB enters

        rows = [e async for e in merged.stream()]
        self.assertEqual(len(rows), 4)                           # union: e0, e1, eA, eB — no dupes
        self.assertTrue(all(e.verify() for e in rows))          # every id matches its content (Law #1)

        st = await StateEngine(merged).reduce()                  # integrity gate sees no tampering
        self.assertEqual(st.get("integrity_broken", []), [])
        self.assertEqual(st.get("entry_count"), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
