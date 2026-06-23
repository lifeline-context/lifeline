"""Prova a montagem: payload responde o quê/por quê/decidido, mostra autoria, trunca explícito (Lei #6)."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry            # noqa: E402
from lifeline.store import SQLiteEventStore  # noqa: E402
from lifeline.state import StateEngine       # noqa: E402
from lifeline.context import ContextAssembler, BOOTSTRAP_HEADER  # noqa: E402


class TestContextAssembler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()
        self.store = SQLiteEventStore(os.path.join(self.dir, "t.db"))
        await self.store.initialize()
        for kind, summary in [
            ("bootstrap", "Funda o Lifeline"),
            ("decision", "DAG content-addressed"),
            ("decision", "status como reducer"),
            ("feature", "ledger SQLite pronto"),
            ("open", "transplantar recall do SDK antigo"),
        ]:
            await self.store.append(Entry(
                author="a", agent="claude-code", provider="anthropic",
                model="claude-opus-4-8", kind=kind, summary=summary,
            ))
        self.engine = StateEngine(self.store)

    async def asyncTearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    async def test_payload_answers_what_why_next(self):
        text = await ContextAssembler(self.engine).assemble()
        self.assertIn("Funda o Lifeline", text)          # o quê
        self.assertIn("DAG content-addressed", text)      # por quê / decidido
        self.assertIn("status como reducer", text)        # por quê / decidido
        self.assertIn("ledger SQLite pronto", text)       # o que vem a seguir

    async def test_payload_shows_authorship(self):
        text = await ContextAssembler(self.engine).assemble()
        self.assertIn("claude-opus-4-8", text)            # qual modelo
        self.assertIn("anthropic", text)                  # qual provider
        self.assertIn("Contributors:", text)              # agregado de autoria

    async def test_payload_shows_open_threads(self):
        text = await ContextAssembler(self.engine).assemble()
        self.assertIn("Open / next", text)
        self.assertIn("transplantar recall do SDK antigo", text)

    async def test_recent_marks_superseded(self):
        # uma thread aberta fechada por correção deve aparecer na "Recente" marcada (fix #0018)
        o = Entry(author="a", agent="claude-code", provider="anthropic",
                  model="m", kind="open", summary="thread efêmera X")
        await self.store.append(o)
        await self.store.append(Entry(author="a", agent="claude-code", provider="anthropic",
                                      model="m", kind="correction", summary="X resolvido", parents=[o.id]))
        text = await ContextAssembler(self.engine).assemble()
        self.assertIn("[closed/reverted]", text)            # marcada como superseded
        # e não aparece mais como aberta
        self.assertNotIn("- `[" + o.id[:8] + "]` thread efêmera X", text)

    async def test_query_adds_relevant_section(self):
        from lifeline.recall import SemanticRecall
        recall = SemanticRecall(self.store)
        text = await ContextAssembler(self.engine).assemble(query="ledger sqlite", recall=recall)
        self.assertIn("Relevant to:", text)
        self.assertIn("ledger SQLite pronto", text)  # relevância lexical achou a entrada certa

    async def test_budget_truncation_is_explicit(self):
        text = await ContextAssembler(self.engine, budget_chars=120).assemble()
        self.assertLessEqual(len(text), 120)
        self.assertIn("truncated", text)

    async def test_budget_drops_decisions_not_recent_or_open(self):
        # Regression: a tight (but not degenerate) budget must drop OLD DECISIONS with an explicit
        # marker — never mid-cut the always-include Open/Recent blocks (Law #6). Build several
        # long-bodied decisions so they cannot all fit, then assert the guaranteed sections survive
        # whole and the safety-net truncation never fires.
        store = SQLiteEventStore(os.path.join(self.dir, "budget.db"))
        await store.initialize()
        await store.append(Entry(author="a", agent="x", provider="p", model="m",
                                 kind="bootstrap", summary="Founds the budget line"))
        for i in range(8):
            await store.append(Entry(
                author="a", agent="x", provider="p", model="m", kind="decision",
                summary=f"decision number {i}", body=("why " * 60).strip()))  # ~240-char body each
        await store.append(Entry(author="a", agent="x", provider="p", model="m",
                                 kind="open", summary="OPENTHREADMARKER stays whole"))
        await store.append(Entry(author="a", agent="x", provider="p", model="m",
                                 kind="feature", summary="RECENTTAILMARKER stays whole"))
        budget = 700
        text = await ContextAssembler(StateEngine(store), budget_chars=budget).assemble()

        self.assertLessEqual(len(text), budget)               # honors the budget
        self.assertNotIn("truncated", text)                   # safety net did NOT fire…
        self.assertIn("older decision(s) omitted", text)      # …decisions were dropped explicitly
        # the always-include blocks are present AND whole (not mid-cut):
        self.assertIn("## Open / next", text)
        self.assertIn("OPENTHREADMARKER stays whole", text)
        self.assertIn("## Recent (what's next)", text)
        self.assertIn("RECENTTAILMARKER stays whole", text)

    async def test_singular_entry_count_pluralization(self):
        one = SQLiteEventStore(os.path.join(self.dir, "one.db"))
        await one.initialize()
        await one.append(Entry(author="a", agent="x", provider="p", model="m",
                               kind="note", summary="only one"))
        text = await ContextAssembler(StateEngine(one)).assemble()
        self.assertIn("1 entry ·", text)        # singular, not "1 entries"
        self.assertNotIn("1 entries", text)

    async def test_empty_ledger_is_graceful(self):
        # primeira execução (ledger vazio) → payload válido com placeholder, sem crash
        empty = SQLiteEventStore(os.path.join(self.dir, "empty.db"))
        await empty.initialize()
        text = await ContextAssembler(StateEngine(empty)).assemble()
        self.assertIn("no bootstrap entry", text)
        self.assertIn("0 entries", text)

    async def test_empty_ledger_shows_bootstrap_cta(self):
        # brownfield: line vazia → o contexto entrega o CTA de bootstrap (gatilho do checkpoint)
        empty = SQLiteEventStore(os.path.join(self.dir, "fresh.db"))
        await empty.initialize()
        text = await ContextAssembler(StateEngine(empty)).assemble()
        self.assertIn(BOOTSTRAP_HEADER, text)            # bloco de bootstrap presente
        self.assertIn("GRANULAR", text)                # protocolo: entradas granulares (não bloco único)
        self.assertIn("Do NOT infer", text)                # guardrail: nunca inferir do código (Leis #1/#5)
        self.assertIn("HITL", text)                      # entra como proposta; humano aprova

    async def test_bootstrap_cta_absent_when_populated(self):
        # já há identidade + decisões → o CTA NÃO aparece (não polui quem já tem contexto)
        text = await ContextAssembler(self.engine).assemble()
        self.assertNotIn(BOOTSTRAP_HEADER, text)

    async def test_bootstrap_cta_persists_with_only_a_stray_note(self):
        # nota solta, sem bootstrap nem decisão → ainda conta como "vazia" p/ fins de contexto
        only_note = SQLiteEventStore(os.path.join(self.dir, "note.db"))
        await only_note.initialize()
        await only_note.append(Entry(author="a", agent="x", provider="p", model="m",
                                     kind="note", summary="conversa solta"))
        text = await ContextAssembler(StateEngine(only_note)).assemble()
        self.assertIn(BOOTSTRAP_HEADER, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
