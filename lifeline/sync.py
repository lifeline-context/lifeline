"""Tier 0 do M3 — sync via GIT, custo zero. Reusa o fato (#0022) de que a view textual
(LIFELINE.md) é o artefato versionado e o `.db` é cache reconstruível: o git move o texto,
o content-addressing torna o merge tolerante a conflito (appends de lados diferentes
deduplicam por id na re-ingestão), e o GitHub vira o hub. Sem infra nova.

Estes são wrappers finos sobre o `git` (subprocess). A orquestração (rebuild antes do push,
migrate+rebuild depois do pull) vive na CLI.
"""
import os
import subprocess


def _git(args, cwd="."):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def is_repo(cwd=".") -> bool:
    return _git(["rev-parse", "--is-inside-work-tree"], cwd).returncode == 0


def _view_files(cwd):
    """Só as views do Lifeline (LIFELINE.md + LIFELINE.<line>.md) — o que o sync move."""
    return [f for f in os.listdir(cwd)
            if f == "LIFELINE.md" or (f.startswith("LIFELINE.") and f.endswith(".md"))]


def add_commit(cwd, message):
    # Stage CIRÚRGICO (auditoria): `git add -A` varria a árvore inteira — WIP, segredos,
    # qualquer sujeira não-commitada entrava num commit chamado "lifeline: sync". O sync só
    # tem mandato sobre as views do ledger; é só isso que ele toca.
    views = _view_files(cwd)
    if views:
        _git(["add", "--", *views], cwd)
    return _git(["commit", "-m", message], cwd)    # returncode != 0 se não houver nada a commitar


def push(cwd, remote="origin"):
    return _git(["push", remote, "HEAD"], cwd)


def pull(cwd, remote="origin"):
    return _git(["pull", "--no-edit", remote], cwd)


def clone(url, dest):
    return _git(["clone", url, dest])


def has_conflict(cwd=".") -> bool:
    """True se há arquivos com conflito de merge não resolvido."""
    r = _git(["diff", "--name-only", "--diff-filter=U"], cwd)
    return bool(r.stdout.strip())
