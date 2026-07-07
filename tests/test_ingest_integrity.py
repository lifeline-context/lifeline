"""Integridade do caminho texto→store (auditoria): (1) o formato novo respeita `parents`
EXPLÍCITO — inclusive vazio (um root no meio do stream não ganha pai espúrio; sem isso o
round-trip muda o id e o `promote`-as-root quebraria); (2) o `recorded_id` da view é
CONFERIDO contra o id recomputado — view editada à mão avisa (e falha com strict), em vez
de re-hashear em silêncio com o `verify` passando."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry                        # noqa: E402
from lifeline.store import SQLiteEventStore             # noqa: E402
from lifeline.projection import render_ledger_markdown  # noqa: E402
from lifeline.ingest import ingest_text                 # noqa: E402


def _e(summary, body="why", kind="decision", parents=None):
    return Entry(author="a", agent="x", provider="p", model="m",
                 kind=kind, summary=summary, body=body, parents=parents or [])


class TestIngestIntegrity(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()

    async def asyncTearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    async def _store(self, name):
        s = SQLiteEventStore(os.path.join(self.dir, name))
        await s.initialize()
        return s

    async def test_midstream_root_round_trips_without_spurious_parent(self):
        # e3 is a legitimate ROOT in the middle of the stream (what `promote` produces).
        src = await self._store("src.db")
        e1 = _e("first root", kind="bootstrap")
        await src.append(e1)
        e2 = _e("chained", parents=[e1.id])
        await src.append(e2)
        e3 = _e("promoted root")                          # parents=[] mid-stream
        await src.append(e3)

        md = await render_ledger_markdown(src)
        dst = await self._store("dst.db")
        n = await ingest_text(md, dst)
        self.assertEqual(n, 3)

        back = {e.id: e async for e in dst.stream()}
        self.assertIn(e3.id, back)                        # id reproduced exactly…
        self.assertEqual(back[e3.id].parents, [])         # …and STILL a root (no prev_id injected)
        self.assertIn(e2.id, back)
        self.assertEqual(back[e2.id].parents, [e1.id])

    async def test_hand_edited_view_warns_by_default(self):
        src = await self._store("src.db")
        await src.append(_e("root", kind="bootstrap"))
        e = _e("decision X", body="the honest why")
        await src.append(e)

        md = await render_ledger_markdown(src)
        tampered = md.replace("the honest why", "a FORGED why")   # recorded id now stale

        dst = await self._store("dst.db")
        with self.assertLogs("lifeline.ingest", level="WARNING") as logs:
            n = await ingest_text(tampered, dst)
        self.assertEqual(n, 2)                                    # ingests (content wins)…
        self.assertIn("doesn't match", "\n".join(logs.output))    # …but says so, loudly
        ids = {x.id async for x in dst.stream()}
        self.assertNotIn(e.id, ids)                               # forged content got a NEW id

    async def test_hand_edited_view_fails_with_strict(self):
        src = await self._store("src.db")
        await src.append(_e("root", kind="bootstrap"))
        await src.append(_e("decision X", body="the honest why"))
        tampered = (await render_ledger_markdown(src)).replace("the honest why", "a FORGED why")

        dst = await self._store("dst.db")
        with self.assertRaises(ValueError):
            await ingest_text(tampered, dst, strict=True)

    async def test_clean_view_round_trips_silently(self):
        src = await self._store("src.db")
        await src.append(_e("root", kind="bootstrap"))
        await src.append(_e("decision X"))
        md = await render_ledger_markdown(src)
        dst = await self._store("dst.db")
        n = await ingest_text(md, dst, strict=True)               # strict passes on a clean view
        self.assertEqual(n, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
