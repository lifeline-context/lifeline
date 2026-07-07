"""Prova o Tier 0 (git sync) ponta a ponta com um repo bare local — sem rede:
log + push no projeto A → clone em B → a line propaga. E checagens leves de sync."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lifeline import sync                                   # noqa: E402
from lifeline.cli import cmd_log, cmd_push, cmd_clone        # noqa: E402
from lifeline.store import SQLiteEventStore                  # noqa: E402


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


class TestSyncBasics(unittest.TestCase):
    def test_is_repo_false_outside_repo(self):
        d = tempfile.mkdtemp()
        try:
            self.assertFalse(sync.is_repo(d))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_add_commit_stages_only_lifeline_views(self):
        # Auditoria: `git add -A` varria a árvore toda — WIP/segredos entravam num commit
        # "lifeline: sync". O stage tem de ser cirúrgico: só LIFELINE.md + LIFELINE.<line>.md.
        d = tempfile.mkdtemp()
        try:
            _git(["init", "-b", "main"], d)
            _git(["config", "user.email", "t@t"], d)
            _git(["config", "user.name", "t"], d)
            for name, content in [("LIFELINE.md", "view"), ("LIFELINE.strategy.md", "view2"),
                                  ("secrets.env", "TOKEN=leak"), ("wip.py", "draft")]:
                with open(os.path.join(d, name), "w") as f:
                    f.write(content)
            sync.add_commit(d, "lifeline: sync")
            committed = _git(["ls-tree", "-r", "--name-only", "HEAD"], d).stdout.split()
            self.assertIn("LIFELINE.md", committed)
            self.assertIn("LIFELINE.strategy.md", committed)
            self.assertNotIn("secrets.env", committed)     # a sujeira NÃO entra
            self.assertNotIn("wip.py", committed)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestGitRoundtrip(unittest.IsolatedAsyncioTestCase):
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

    async def test_push_then_clone_propagates_line(self):
        os.chdir(self.A)
        await cmd_log(os.path.join(".lifeline", "ledger.db"), "LIFELINE.md",
                      "decision", "usar gRPC", "porque escala", "me",
                      "claude-code", "anthropic", "m", None)
        ok, msg = await cmd_push(os.path.join(".lifeline", "ledger.db"), "LIFELINE.md")
        self.assertTrue(ok, f"push falhou: {msg}")
        os.chdir(self.prev)

        B = os.path.join(self.root, "B")
        ok2, msg2 = await cmd_clone(self.bare, B)
        self.assertTrue(ok2, f"clone falhou: {msg2}")

        store = SQLiteEventStore(os.path.join(B, ".lifeline", "ledger.db"))
        await store.initialize()
        summaries = [e.summary async for e in store.stream()]
        self.assertIn("usar gRPC", summaries)  # a line cruzou A → bare → B


if __name__ == "__main__":
    unittest.main(verbosity=2)
