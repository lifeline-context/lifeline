# Getting started

Lifeline is a **context runtime for AI-assisted development** — *git for reasoning*. It keeps an
append-only, content-addressed, anchored ledger of your project's **why** and delivers it to any AI
over MCP, so a fresh model connects and **already knows**.

## Install

```bash
pip install lifeline-context        # the lifeline CLI + lifeline-mcp server
pip install -e .                    # from the repo root (dev)
pip install -e ".[cloud]"           # optional: cloud mode (Supabase)
pip install -e ".[embeddings]"      # optional: dense semantic recall
```

Dependencies: `pydantic`, `aiosqlite`, `mcp`, `httpx`. **Python ≥ 3.10.** The core is local,
single-user, and zero-dependency for recall by default.

## Quickstart (CLI)

Each project gets its own `.lifeline/ledger.db`:

```bash
lifeline log --kind bootstrap --summary "Bootstrap project X" --body "Multi-tenant billing API."
lifeline log --kind decision  --summary "DB: PostgreSQL"      --body "ACID required by audit."

lifeline context                    # the assembled current truth (what an AI reads)
lifeline context --query "database" # prioritizes what's relevant to the task (Layer 3)
lifeline verify                     # checks the chain's integrity → OK
```

`LIFELINE.md` regenerates on every `log` — **don't hand-edit it**. On a fresh clone without
`.lifeline/`, rebuild the cache with `lifeline migrate --from LIFELINE.md`.

## The loop (do both sides)

- **On connect:** load the context (`lifeline context` or the MCP resource) *before* acting.
- **While working:** on each meaningful decision / fix / incident, **append** (`lifeline log` or
  `lifeline_append`). Reversed something? `lifeline_recontextualize` supersedes it by id.

## Connect it to your AI

Lifeline ships a local MCP server (`lifeline-mcp`, stdio). On connect, the AI gets the
`lifeline://project/context` resource plus tools — and the write tools are **human-in-the-loop**:
they *propose*, a human *approves*. **Claude Code reads `.mcp.json` automatically:**

```json
{ "mcpServers": { "lifeline": {
    "command": "lifeline-mcp", "args": [],
    "env": { "LIFELINE_DB": ".lifeline/ledger.db" } } } }
```

Cursor, Claude Desktop, and Gemini CLI use copy-paste snippets — see [Integration](integration.html).
Web chat apps (claude.ai, ChatGPT) need a remote server + OAuth — see [MCP & remote](mcp.html).

## Adopting mid-project (brownfield)

Lifeline records the *why* **going forward** — it never reconstructs it from your code or git
history. So a fresh install on a live project starts **empty**. Run `lifeline init` (or just connect
your AI — the empty context prints the same call-to-action). It walks you through a one-time
**bootstrap checkpoint**, human-in-the-loop:

1. **Read** the reasoning artifacts you already wrote (README, ADRs, PR descriptions). The *why* is
   never inferred from code or diffs (Laws 1 & 5).
2. **Ask** 3–7 short why-questions — only the tacit reasoning that isn't written down.
3. **Propose** the checkpoint as *granular* entries: 1 `bootstrap` + N `decision` + M `open`. You
   approve the batch. Nothing enters unapproved.

After that, the loop runs forward.

## Local → cloud (graduation)

Everything is content-addressed, so pushing a local line to the cloud is **lossless and
idempotent** — same ids, re-seed dedupes itself.

```bash
lifeline --store supabase migrate --from LIFELINE.md   # seed (repeatable — no dupes)
lifeline --store supabase context                       # operate against the cloud
```

Just want to share the *text* (no cloud)? `lifeline push` (Tier 0 — git sync).
