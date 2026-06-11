# CLI reference

Globals: `--db` (default `.lifeline/ledger.db`, or `LIFELINE_DB` env) · `--line <name>` maps a named
line (ledger **and** view together: `.lifeline/<name>.db` + `LIFELINE.<name>.md`) ·
`--store {sqlite,supabase}` (default `sqlite`). Identity on a write is set with `--author` /
`--agent` / `--provider` / `--model` (who/what is proposing).

| Command | What it does |
|---|---|
| `lifeline init` | **adopting mid-project (brownfield):** initialize the line + print the bootstrap protocol (a HITL context checkpoint) |
| `lifeline log --kind … --summary … [--body … --parents id,…]` | **human:** append directly to the line (you're the approver) + regenerate the view |
| `lifeline propose --kind … --summary … --body …` | propose an entry (**HITL**) — stays pending, not in the line |
| `lifeline review` · `approve <pid\|all>` · `reject <pid\|all>` | HITL curation: list / seal / discard |
| `lifeline context [--query "…"] [--budget N]` | print the assembled current truth (relevance if `--query`); `--budget` defaults to **8000** chars |
| `lifeline verify` | check that every id matches its content |
| `lifeline rebuild` · `migrate --from LIFELINE.md` | regenerate the view / rebuild the `.db` from markdown |
| `lifeline schema` | print the bundled Supabase schema (cloud) |
| `lifeline lines` | list the project's lines (`.lifeline/*.db`) |
| `lifeline push` · `pull` · `clone <url> <dir>` | **git sync** (Tier 0, zero cost): the text view syncs; the `.db` rebuilds |

> With `--store supabase`, the cloud is the source — `push` / `pull` / `clone` / `lines` are
> **local-only** and not available there; use `log`, `context`, `verify`, `rebuild`, `migrate`.
> `lifeline init` is **idempotent** (re-running won't clobber an existing line). Dense recall is
> opt-in: `pip install "lifeline-context[embeddings]"` + `LIFELINE_EMBEDDER=dense`.

## Write tiering (like approving a shell command)

The human's `log` commits directly — they're the approver. The **AI via MCP `propose`** enters as a
**pending** proposal (HITL); a human **approves** before it becomes truth. Write-time anti-junk
requires the *why* (the `--body`), so junk never enters the line.

## Kinds

`bootstrap` (project identity) · `decision` · `feature` · `fix` · `incident` · `milestone` ·
`release` · `note` · `open` (an open thread) · `correction` (supersedes its parents).

## A line

One reasoning ledger (code *or* conversation). A project has 1 by default and supports N via
`--line <name>` — no collisions between them.
