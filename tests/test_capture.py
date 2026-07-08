"""Prova o `lifeline capture` (F1, zero-LLM): rascunha propostas das MENSAGENS de commit —
o corpo humano é o porquê (sem corpo, abstém; Lei #5), kind pelo prefixo convencional,
idempotente via capture.head, e tudo entra PENDENTE (HITL) — nunca direto na line."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline import cli                        # noqa: E402
from lifeline.cli import cmd_capture, cmd_review, cmd_verify  # noqa: E402


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def _commit(cwd, subject, body="", n=[0]):
    n[0] += 1
    path = os.path.join(cwd, f"f{n[0]}.txt")
    with open(path, "w") as f:
        f.write(str(n[0]))
    _git(["add", "."], cwd)
    msg = f"{subject}\n\n{body}" if body else subject
    _git(["commit", "-m", msg], cwd)


class TestLocalCapture(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir = tempfile.mkdtemp()
        _git(["init", "-b", "main"], self.dir)
        _git(["config", "user.email", "t@t"], self.dir)
        _git(["config", "user.name", "t"], self.dir)
        self.db = os.path.join(self.dir, ".lifeline", "ledger.db")
        os.makedirs(os.path.dirname(self.db))
        self.prev = os.getcwd()
        os.chdir(self.dir)                       # capture usa o repo do cwd

    async def asyncTearDown(self):
        os.chdir(self.prev)
        shutil.rmtree(self.dir, ignore_errors=True)

    async def test_captures_commits_with_a_written_why(self):
        _commit(self.dir, "feat(auth): single-flight token refresh",
                "Tokens looped forever because refresh raced logout; single-flighting fixes it.")
        _commit(self.dir, "chore: bump deps")                     # sem corpo → abstém
        _commit(self.dir, "fix: stop double-charge",
                "Retries lacked an idempotency key, so a timeout could charge twice.\n\n"
                "Co-Authored-By: Bot <b@x>")
        proposed, skipped = await cmd_capture(self.db, "me")
        self.assertEqual(len(proposed), 2)                        # só os com porquê
        self.assertEqual(skipped, 1)
        kinds = sorted(k for _, k, _ in proposed)
        self.assertEqual(kinds, ["feature", "fix"])               # prefixo convencional → kind
        pend = await cmd_review(self.db)
        self.assertEqual(len(pend), 2)                            # PENDENTE (HITL)…
        _ok, n, _, _ = await cmd_verify(self.db)
        self.assertEqual(n, 0)                                    # …e NADA selado na line
        bodies = [p["body"] for p in pend]
        self.assertTrue(all("[captured from commit " in b for b in bodies))   # proveniência
        self.assertFalse(any("Co-Authored-By" in b for b in bodies))          # trailer fora

    async def test_rerun_is_idempotent_and_new_commits_flow(self):
        _commit(self.dir, "feat: outbox", "Dual writes dropped events; outbox gives at-least-once.")
        p1, _ = await cmd_capture(self.db, "me")
        self.assertEqual(len(p1), 1)
        p2, s2 = await cmd_capture(self.db, "me")                 # re-rodar: nada novo
        self.assertEqual((len(p2), s2), (0, 0))
        _commit(self.dir, "fix: race", "The relay double-fired on restart; now it locks the batch.")
        p3, _ = await cmd_capture(self.db, "me")
        self.assertEqual(len(p3), 1)                              # só o commit NOVO
        self.assertEqual(len(await cmd_review(self.db)), 2)

    async def test_utf8_commit_bodies_survive_on_any_locale(self):
        # Checkpoint finding: on Windows, subprocess text-mode decoded git output with the
        # locale codepage (cp1252) — a body with "✓"/"č" CRASHED the reader thread. sync._git
        # now pins UTF-8; the why must come back intact.
        _commit(self.dir, "feat: acentuação",
                "porquê: auditoria exige ACID — decisão validada č ✓ em produção.")
        proposed, skipped = await cmd_capture(self.db, "me")
        self.assertEqual(len(proposed), 1)
        body = (await cmd_review(self.db))[0]["body"]
        self.assertIn("porquê", body)
        self.assertIn("✓", body)                                  # UTF-8 intacto, sem mojibake

    async def test_outside_a_repo_fails_loud(self):
        os.chdir(self.prev)
        outside = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside, True)
        os.chdir(outside)
        with self.assertRaises(ValueError):
            await cmd_capture(os.path.join(outside, "x.db"), "me")


if __name__ == "__main__":
    unittest.main(verbosity=2)
