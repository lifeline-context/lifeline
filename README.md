# Lifeline

> **A context runtime for AI-assisted development.** The project stores *why* it is what it
> is — and any AI connects and **already knows**, with no human re-explaining.

🌐 **English** · [Português](README.pt-BR.md)

[![pypi](https://img.shields.io/pypi/v/lifeline-context)](https://pypi.org/project/lifeline-context/) ![status](https://img.shields.io/badge/status-beta-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![tests](https://img.shields.io/badge/tests-153%20passing-brightgreen) ![license](https://img.shields.io/badge/license-FSL--1.1--MIT-blue)

In one line, it's **"git for reasoning"**: just as git versions *what* changed in the code,
Lifeline versions *why* — decisions, reversals, incidents, the current state — in an
append-only, content-addressed ledger that lives inside the project. Any model (Claude, GPT,
Gemini), in any session, reconstructs the context the moment it connects via MCP.

> **Use Claude Code?** It reads `.mcp.json` **automatically** — `pip install lifeline-context`, drop
> the [snippet below](#connect-it-to-your-ai-zero-config-in-claude-code) into your repo, and your AI
> connects to the project's full *why* with **zero config**. (Cursor, Claude Desktop, Gemini CLI, and
> web chat work too — see below.)

---

## The problem

AI assistants are **stateless across sessions**. With every new session, agent, or provider,
the human becomes the memory bus — re-explaining decisions that already existed. The naive
fix (a living markdown log) works until it blows past the context window. "Memory" tools
store text/vectors with no provenance → hallucinated recall.

## The idea

The **north star** is a single metric — **Time-to-Context (TTC) → 0** — operationalized by an
acceptance test:

> A fresh AI connects, **with no human in the loop**, and correctly answers:
> **what / why / what's decided / what's next?**

Lifeline keeps the project's "lifeline" (the `LIFELINE.md`) and makes it **queryable,
compressible, and anchored** — so it never overflows the window and never hallucinates.

---

## Install

```bash
pip install lifeline-context        # installs lifeline, lifeline-mcp, lifeline-mcp-remote
pip install -e .                    # or, from the repo root (dev)
pip install -e ".[cloud]"           # optional: cloud mode (Supabase) — pulls httpx explicitly
```

Dependencies: `pydantic`, `aiosqlite`, `mcp`, `httpx`. Python ≥ 3.10.

## Quickstart (CLI)

```bash
# In ANY of your projects — each gets its own .lifeline/ledger.db:
lifeline log --kind bootstrap --summary "Bootstrap project X"   --body "Multi-tenant billing API."
lifeline log --kind decision  --summary "DB: PostgreSQL"        --body "ACID required by audit."
lifeline log --kind open      --summary "Queue: SQS vs RabbitMQ" --body "Decide after the load test."

lifeline context                       # prints the assembled current truth (what an AI reads)
lifeline context --query "database"    # prioritizes what's relevant to the task (Layer 3)
lifeline verify                        # checks the chain's integrity
```

…and `lifeline context` prints exactly what a fresh AI reads (real output, no mockup):

```text
# Lifeline — project context
**What:** Bootstrap project X  _(founded by none/human)_
_3 entries · head 99676780_

## Open / next
- `[99676780]` Queue: SQS vs RabbitMQ

## Why / what's decided (decisions in force)
- **DB: PostgreSQL** `[b023ddc6]` — _none/human_
  > ACID required by audit.

## Recent (what's next)
- [bootstrap] Bootstrap project X
- [decision] DB: PostgreSQL
- [open] Queue: SQS vs RabbitMQ
```

Every line is anchored to its event id (`[b023ddc6]`) — the AI can verify it, not just trust it.

`LIFELINE.md` regenerates on every `log` — **don't hand-edit it**. On a fresh clone without
`.lifeline/`, rebuild the cache with `lifeline migrate --from LIFELINE.md`.

**Adopting mid-project (brownfield)?** Lifeline records the *why* **going forward** — it does not
reconstruct it from your code or git history. So a fresh install on a live project starts **empty**.
Run `lifeline init` (or just connect your AI — the empty context prints the same call-to-action): it
walks you through a one-time **bootstrap checkpoint** — your AI reads your existing reasoning docs
(README, ADRs, PR descriptions), asks a few *why* questions, and **proposes** granular entries (HITL)
that you approve. After that, the loop runs forward. The *why* is never inferred from code (Laws #1/#5).

## Connect it to your AI (zero config in Claude Code)

Lifeline ships a local **MCP server** (`lifeline-mcp`, stdio). On connect, the AI gets the
`lifeline://project/context` resource + tools (`lifeline_recall`, and write tools that are
**HITL** — they *propose*; the human approves). Server config is in [`.mcp.json`](.mcp.json):

```json
{ "mcpServers": { "lifeline": {
    "command": "lifeline-mcp", "args": [],
    "env": { "LIFELINE_DB": ".lifeline/ledger.db" } } } }
```

- **Claude Code** reads `.mcp.json` **automatically**.
- **Cursor / Claude Desktop / Gemini CLI:** copy-paste snippets in [`docs/INTEGRATION.md`](docs/INTEGRATION.md).
- **Web chat apps** (claude.ai, ChatGPT) need a remote server + OAuth — see [`docs/MCP_REMOTE.md`](docs/MCP_REMOTE.md).

## Quickstart (Python SDK)

```python
import asyncio
from lifeline import Entry, SQLiteEventStore, StateEngine, ContextAssembler, SemanticRecall

async def main():
    store = SQLiteEventStore(".lifeline/ledger.db")
    await store.initialize()
    await store.append(Entry(kind="decision", author="me",
                             summary="DB: PostgreSQL", body="ACID for audit."))
    ctx = await ContextAssembler(StateEngine(store)).assemble()   # ready to inject into a prompt
    print(ctx)
    hits = await SemanticRecall(store).search("which database", k=3)  # anchored relevance

asyncio.run(main())
```

---

## The loop (do both sides)

- **On connect:** load the context (`lifeline context` or the MCP resource) before acting.
- **While working:** on each decision/feature/fix/incident, **append** (`lifeline log` or
  `lifeline_append`). Reversed something? `lifeline_recontextualize` (supersede by id).

```
   CONNECT (read)                                                      WRITE (append)
   lifeline context        ┌─────────────┐  reduce  ┌──────────┐  rank+  lifeline log
   MCP resource ──────────▶│  Layer 1    │─────────▶│ Layer 2  │ budget  lifeline_append
   lifeline://…/context    │  Ledger     │          │ State    │────────▶ (HITL: propose)
   Layer 3 (recall) ──────▶│  (immutable │          │ (current │
   anchored relevance      │   DAG)      │          │  truth)  │
                           └──────┬──────┘          └────┬─────┘
                                  │ projection (store → markdown) ▼
                                  └──────────────▶ LIFELINE.md (generated view, git-diffable)
```

## Core concepts

- **Entry** — the atomic unit. Content-addressed: `id = sha256(kind, author, agent, provider,
  model, summary, body, sorted-parents)`. `ts` and `dedup_key` are **outside** the hash → the
  same content yields the same `id` on any machine (the basis for dedup and sync).
- **3 memory layers** (all anchored to the immutable ledger): **Ledger** (hashed append-only
  DAG, source of truth) · **State** (current truth reduced via reducers; status is a
  projection, not a state machine) · **Recall** (relevance search; every hit anchored to its
  source event).
- **Supersession** — a `correction` referencing another entry's `id` removes it from the
  current truth (reverted decision, closed thread). Append-only: the past is never edited.
- **Anti-hallucination anchor** — every item the AI reads carries its source event's hash.
  No anchor, no entry.

Full detail in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## CLI reference

| Command | What it does |
|---|---|
| `lifeline init` | **adopting mid-project (brownfield):** initialize the line + print the bootstrap protocol (a HITL context checkpoint) |
| `lifeline log --kind … --summary … [--body … --parents id,…]` | **human:** append directly to the line (you're the approver) + regenerate the view |
| `lifeline propose --kind … --summary … --body …` | propose an entry (**HITL**) — stays pending, not in the line |
| `lifeline review` · `approve <pid\|all>` · `reject <pid\|all>` | HITL curation: list / seal / discard |
| `lifeline context [--query "…"] [--budget N]` | print the assembled current truth (relevance if `--query`) |
| `lifeline verify` | check that every `id` matches its content |
| `lifeline rebuild` · `migrate [--strict] --from LIFELINE.md` | regenerate the view / rebuild the `.db` from markdown (`--strict` fails if a recorded id doesn't match its content — tamper check) |
| `lifeline schema` | print the bundled Supabase SQL schema (paste into the SQL Editor for cloud mode) |
| `lifeline lines` | list the project's lines (local `.lifeline/*.db`, or the cloud's with `--store supabase`) |
| `lifeline promote --from <line> --to <line> --id <id>[,…] \| --kind <kind>` | copy entries across lines as roots — **idempotent** (same content → same id, re-promoting dedups) |
| `lifeline push` · `pull` · `clone <url> <dir>` | **git sync** (Tier 0, zero cost): the text view syncs; the `.db` rebuilds |

**Write tiering (like approving a shell command):** the human's `log` commits directly (they're
the approver); the **AI via MCP `propose`** enters as a **pending** proposal (HITL), and a human
**approves** before it becomes truth. Write-time anti-junk requires the *why*; junk never enters.

**Globals:** `--db` (default `.lifeline/ledger.db`) · **`--line <name>`** · `--store {sqlite,supabase}`
· identity on a write (`--author` / `--agent` / `--provider` / `--model`).

### Lines — parallel ledgers

A **line** is one independent reasoning ledger (its own DAG + view). A project has **one by default**
— `ledger` → `LIFELINE.md` — and adds as many as you want with `--line <name>`: each is a fully
separate ledger **and** view (`.lifeline/<name>.db` + `LIFELINE.<name>.md`), with no collisions.
**Every** command takes `--line`, and a line is **created on its first write** (no setup step).

```bash
# Your project's MAIN line (code reasoning) → LIFELINE.md
lifeline log --kind decision --summary "Auth: JWT over sessions" --body "Stateless; scales out."

# A PARALLEL line for a different context (business plan) → LIFELINE.businessplan.md
lifeline --line businessplan log --kind decision \
  --summary 'Pricing: $20/seat/mo' --body "Covers infra at ~50 seats; undercuts incumbents."

lifeline --line businessplan context   # assembles ONLY the businessplan reasoning
lifeline --line businessplan verify     # each line verifies independently
lifeline lines                          # ledger → LIFELINE.md · businessplan → LIFELINE.businessplan.md
```

Keep separate **contexts** in separate lines — code vs. business plan vs. a subsystem or an
experiment — so each *why* lives where it belongs and stays diff-able on its own. To point your
**AI at a specific line over MCP**, set `LIFELINE_LINE=businessplan` in the server's env.

## Local → cloud (graduation)

Everything is content-addressed → **pushing a local line to the cloud is lossless and
idempotent**: same ids, re-seed dedupes itself.

```bash
lifeline --store supabase migrate --from LIFELINE.md   # seed (repeatable — no dupes)
lifeline --store supabase context                       # now operate against the cloud
```

Just share the *text* (no cloud)? `lifeline push` (Tier 0 — git). Cloud setup + auth:
[`docs/M3_TIER1_SUPABASE.md`](docs/M3_TIER1_SUPABASE.md) · `.env.example`.

## The 7 laws (the constitution)

1. **No memory without an immutable anchor** (anti-hallucination). 2. **Append-only** (corrections
are new entries). 3. **Deterministic content-addressing.** 4. **Provider-agnostic storage; deliver
in the provider's format.** 5. **The *why* outweighs the *what*.** 6. **Budget is first-class**
(truncation always explicit). 7. **MCP-native.**

**Non-goals:** Lifeline is NOT a cognitive OS, MMU, agent orchestrator/sandbox, workflow engine,
a git replacement, an executor/curator (self-healing), or a trainer (fine-tuning). **It records
reasoning, not execution.**

## Status & roadmap

**Beta.** Solid, proven **local single-user** core — correctness locked by tests (determinism,
anti-tamper, omission detection, supersession + un-supersession, round-trip fixed-point, recall
abstention, concurrent-append idempotency). **Cloud (M3) functional and live-validated.** 153
tests green (147 offline + 6 live-gated); CI on GitHub Actions.

| Milestone | State |
|---|---|
| **M1 / M1.5** — the loop (ledger→state→assembly→MCP), authorship, recall, CLI, store-is-source | ✅ done |
| **M3 Tier 0** — git sync | ✅ done |
| **M3 Tier 1** — Supabase store + append-only RLS + cloud HITL | ✅ live-validated |
| **M3** — remote MCP (HTTP/SSE) + OAuth **Resource Server** (multi-tenant) | ✅ done |
| **M2** — dense semantic embedder (default is lexical) | ✅ opt-in (`pip install lifeline-context[embeddings]`, #0029) |
| **Gap audit** — prefix-resolution, read-time anchor verify, omission detection, dense abstention, lossless round-trip | ✅ done |
| **Hosted-connector auth** — Resource Server validating Supabase's native **OAuth 2.1 Server** (DCR + auth-code/PKCE) via JWKS; bundled custom AS as a fallback (`LIFELINE_OAUTH_AS=1`) | ✅ done |
| **M4** — multi-user (concurrent DAG merge) / hub | planned |

**Honest limits today:** recall defaults to lexical (keywords); a **dense semantic** embedder is
opt-in (`pip install lifeline-context[embeddings]`, then `LIFELINE_EMBEDDER=dense`, #0029).
Hosted web-chat connectors work via Supabase's native OAuth Server (the remote MCP is a Resource
Server) — the path is wired, unit-tested, and **validated live** end-to-end (a real connector
gets `401` without a token and `200` with a valid Supabase JWT; #0049, #0079, #0090). A turnkey
**paid** cloud still needs billing wired into a hosted plan; today the core is **source-available +
bring-your-own-Supabase**. No retry/backoff in the cloud adapter yet (log+raise only).

## Built by dogfooding

Lifeline was rebuilt **using itself from entry #0001**: every decision became an anchored entry
in `LIFELINE.md`. The process surfaced **real bugs in actual use** that unit tests missed
(taxonomy, encoding, false relevance) — all recorded. The proof it works is that the repo needs
no one to explain it.

## Contributing & license

The rule is the constitution: **if you touched it, append to the line.** See
[`CONTRIBUTING.md`](CONTRIBUTING.md) · [`AGENTS.md`](AGENTS.md) · [`llms.txt`](llms.txt).

**License:** [FSL-1.1-MIT](LICENSE) (Functional Source License) — **source-available**: read it,
run it, modify it, self-host it for any purpose *except* offering it as a competing commercial
service; it **converts to MIT two years** after each release. (Versions ≤ 0.2.0 were published
under MIT and stay MIT.) The paid layer is the hosted **hub**, not the code.
