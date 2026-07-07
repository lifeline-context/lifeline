"""Prova que o Entry obedece a Lei #3 (content-addressing determinístico)."""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline.entry import Entry  # noqa: E402


def make(**kw):
    base = dict(kind="decision", author="a@x", agent="claude-code",
                provider="anthropic", model="claude-opus-4-8",
                summary="s", body="b")
    base.update(kw)
    return Entry(**base)


class TestEntryDeterminism(unittest.TestCase):
    def test_id_is_stable_across_ts(self):
        """Mesmo conteúdo em momentos diferentes → mesmo id (ts fora do hash)."""
        e1 = make()
        time.sleep(0.01)
        e2 = make()
        self.assertNotEqual(e1.ts, e2.ts)
        self.assertEqual(e1.id, e2.id)

    def test_id_sensitive_to_body(self):
        """Mudar o conteúdo muda o id."""
        self.assertNotEqual(make(body="x").id, make(body="y").id)

    def test_id_invariant_to_parent_order(self):
        """Pais [A,B] e [B,A] produzem o mesmo id (set causal, não lista)."""
        self.assertEqual(
            make(parents=["aaa", "bbb"]).id,
            make(parents=["bbb", "aaa"]).id,
        )

    def test_parents_change_id(self):
        self.assertNotEqual(make(parents=[]).id, make(parents=["aaa"]).id)

    def test_self_verifies(self):
        self.assertTrue(make(body="anything").verify())

    def test_dedup_key_excluded_from_id(self):
        """dedup_key é metadado de idempotência — não muda a identidade."""
        self.assertEqual(make(dedup_key="k1").id, make(dedup_key="k2").id)

    def test_stored_id_is_preserved(self):
        """Reconstruir com id explícito não recomputa (preserva o storage)."""
        e = Entry(id="deadbeef", kind="note", author="a", summary="s")
        self.assertEqual(e.id, "deadbeef")
        self.assertFalse(e.verify())  # id não bate com o conteúdo → detectável


class TestCanonicalInjectivity(unittest.TestCase):
    """The canonical form must be INJECTIVE: two distinct Entries can never share an id.
    The old join-by-newline scheme provably collided (audit finding #1) — these lock the fix."""

    def test_audited_collision_is_closed(self):
        # The exact pair proven to collide under the old scheme: a "\n" inside a field shifted
        # every boundary, making (agent="b\nc", ...) equal (..., body="f\ng") byte-for-byte.
        a = Entry(kind="decision", author="a", agent="b\nc", provider="d",
                  model="e", summary="f", body="g")
        b = Entry(kind="decision", author="a", agent="b", provider="c",
                  model="d", summary="e", body="f\ng")
        self.assertNotEqual(a.id, b.id)

    def test_boundary_characters_do_not_collide(self):
        # No delimiter-looking content ("\n", "|", ":", digits) may merge adjacent fields.
        cases = [
            (make(summary="s\nx", body="b"), make(summary="s", body="x\nb")),
            (make(summary="s|x"), make(summary="s", body="|x" + "\nb")),
            (make(parents=["aa", "bb"]), make(parents=["aa|bb"])),
            (make(parents=["aa", "bb"]), make(parents=["aabb"])),
            (make(summary="3:abc"), make(summary="3", body="abc\nb")),
        ]
        for x, y in cases:
            self.assertNotEqual(x.id, y.id, f"collision: {x.summary!r} vs {y.summary!r}")

    def test_field_shift_does_not_collide(self):
        # Sliding the same text across neighbouring fields must change the id.
        a = make(agent="xy", provider="z")
        b = make(agent="x", provider="yz")
        self.assertNotEqual(a.id, b.id)

    def test_empty_vs_missing_parent_distinct(self):
        self.assertNotEqual(make(parents=[]).id, make(parents=[""]).id)

    def test_utf8_length_is_byte_based(self):
        # Multibyte content must still round-trip: same content → same id; different → different.
        self.assertEqual(make(body="porquê ✓").id, make(body="porquê ✓").id)
        self.assertNotEqual(make(body="porquê ✓").id, make(body="porque v").id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
