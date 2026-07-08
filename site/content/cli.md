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
| `lifeline rebuild` · `migrate [--strict] --from LIFELINE.md` | regenerate the view / rebuild the `.db` from markdown (`--strict` fails on recorded-id mismatch — tamper check) |
| `lifeline schema` | print the bundled Supabase schema (cloud) |
| `lifeline lines` | list the project's lines (local `.lifeline/*.db`, or the cloud's with `--store supabase`) |
| `lifeline promote --from <line> --to <line> --id <id>[,…] \| --kind <kind>` | copy entries across lines as roots — **idempotent** (same content → same id → re-promoting dedups) |
| `lifeline rehash` | one-shot migration after a hash-scheme upgrade: recompute every id, remap parents, backup + verify |
| `lifeline capture [--last N]` | draft proposals from recent **git commit messages** (zero-LLM): the commit body is the *why* — no body, no draft; everything lands **PENDING** (HITL) |
| `lifeline exam [--json]` | **Context Health 0–100**: how ready this line leaves a fresh AI (what/why/decided/next) — integrity gates the score; every gap comes with the command that fixes it |
| `lifeline push` · `pull` · `clone <url> <dir>` | **git sync** (Tier 0, zero cost): the text view syncs; the `.db` rebuilds |

> With `--store supabase`, the cloud is the source — `push` / `pull` / `clone` / `rehash` /
> `promote` are **local-only**; `log`, `context`, `verify`, `rebuild`, `migrate`, and `lines`
> all work against the cloud. `lifeline init` is **idempotent** (re-running won't clobber an
> existing line). Dense recall is opt-in: `pip install "lifeline-context[embeddings]"` +
> `LIFELINE_EMBEDDER=dense`.

## Write tiering (like approving a shell command)

The human's `log` commits directly — they're the approver. The **AI via MCP `propose`** enters as a
**pending** proposal (HITL); a human **approves** before it becomes truth. Write-time anti-junk
requires the *why* (the `--body`), so junk never enters the line.

## Kinds

`bootstrap` (project identity) · `decision` · `feature` · `fix` · `incident` · `milestone` ·
`release` · `note` · `open` (an open thread) · `correction` (supersedes its parents).

## A line

One **independent, content-addressed reasoning ledger** (its own DAG + view). A project has 1 by
default (`ledger` → `LIFELINE.md`) and supports N via `--line <name>` (`.lifeline/<name>.db` +
`LIFELINE.<name>.md`) — no collisions. **Every** command takes `--line`, and a line is **created on
its first write** (no setup step); the MCP server picks one via `LIFELINE_LINE`.

```bash
# MAIN line (code reasoning) → LIFELINE.md
lifeline log --kind decision --summary "Auth: JWT over sessions" --body "Stateless; scales out."

# PARALLEL line (business plan) → LIFELINE.businessplan.md
lifeline --line businessplan log --kind decision \
  --summary 'Pricing: $20/seat/mo' --body "Covers infra at ~50 seats."

lifeline --line businessplan context   # ONLY the businessplan reasoning
lifeline lines                         # ledger → LIFELINE.md · businessplan → LIFELINE.businessplan.md
```

Use separate lines for separate contexts / reasoning threads (and Tree-of-Thoughts) — see
[Concepts → Lines](concepts.html).
