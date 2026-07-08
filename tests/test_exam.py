"""Prova o `lifeline exam` (F2): score determinístico de Context Health. Integridade é
PORTÃO (cadeia quebrada = 0/F — score alto sobre ledger adulterado seria a mentira perfeita);
as demais dimensões medem condições NECESSÁRIAS pra TTC→0."""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry            # noqa: E402
from lifeline.store import SQLiteEventStore  # noqa: E402
from lifeline.cli import cmd_exam            # noqa: E402


def _e(kind, summary, body="", ts=None, parents=None):
    kw = dict(author="a", agent="x", provider="p", model="m",
              kind=kind, summary=summary, body=body, parents=parents or [])
    if ts is not None:
        kw["ts"] = ts
    return Entry(**kw)


class TestExam(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = os.path.join(self.dir, "t.db")

    async def asyncTearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    async def _store(self):
        s = SQLiteEventStore(self.db)
        await s.initialize()
        return s

    def _dim(self, dims, name):
        return next((p, m, d) for n, p, m, d in dims if n == name)

    async def test_healthy_ledger_scores_high(self):
        s = await self._store()
        await s.append(_e("bootstrap", "Founds project X", "why it exists"))
        await s.append(_e("decision", "Postgres over Mongo",
                          "audit requires ACID transactions across tenants"))
        await s.append(_e("open", "pick a KYC provider", "compliance deadline in Q3"))
        score, grade, dims, tips, failed = await cmd_exam(self.db)
        self.assertFalse(failed)
        self.assertGreaterEqual(score, 90)                      # tudo presente e fresco
        self.assertEqual(grade, "A")
        self.assertEqual(self._dim(dims, "why-density")[0], 25)  # 1/1 decisão com porquê
        self.assertEqual(self._dim(dims, "ttc-probe")[0], 15)    # what/why/next/recent

    async def test_empty_ledger_scores_low_with_suggestions(self):
        await self._store()
        score, grade, dims, tips, failed = await cmd_exam(self.db)
        self.assertFalse(failed)
        self.assertLess(score, 40)
        self.assertTrue(any("bootstrap" in t for t in tips))     # diz COMO consertar
        self.assertTrue(any("decision" in t for t in tips))

    async def test_whyless_decisions_hit_density(self):
        s = await self._store()
        await s.append(_e("bootstrap", "X", "why"))
        await s.append(_e("decision", "with why", "a real rationale, long enough to count here"))
        await s.append(_e("decision", "naked decision"))         # sem porquê
        score, _, dims, tips, _ = await cmd_exam(self.db)
        pts, mx, detail = self._dim(dims, "why-density")
        self.assertEqual((pts, mx), (12, 25))                    # 1/2 → 12 (banker's rounding)
        self.assertIn("1/2", detail)
        self.assertTrue(any("no real why" in t for t in tips))

    async def test_stale_ledger_hits_freshness(self):
        s = await self._store()
        old = datetime.now(timezone.utc) - timedelta(days=120)
        await s.append(_e("bootstrap", "X", "why", ts=old))
        await s.append(_e("decision", "D", "a rationale long enough to count as a why", ts=old))
        _, _, dims, tips, _ = await cmd_exam(self.db)
        self.assertEqual(self._dim(dims, "freshness")[0], 0)     # 120d → 0 pontos
        self.assertTrue(any("capture" in t for t in tips))       # aponta o remédio certo

    async def test_tampered_ledger_fails_the_gate(self):
        s = await self._store()
        await s.append(_e("bootstrap", "X", "why"))
        await s.append(_e("decision", "D", "a rationale long enough to count as a why"))
        con = sqlite3.connect(self.db)                            # adultera o conteúdo no disco
        con.execute("update entries set payload = replace(payload, 'ACID', 'acid') "
                    "where payload like '%ACID%'")
        con.execute("update entries set payload = json_set(payload, '$.summary', 'FORGED')")
        con.commit()
        con.close()
        score, grade, dims, tips, failed = await cmd_exam(self.db)
        self.assertTrue(failed)
        self.assertEqual((score, grade), (0, "F"))               # portão: não pontua o resto
        self.assertTrue(any("verify" in t for t in tips))


if __name__ == "__main__":
    unittest.main(verbosity=2)
