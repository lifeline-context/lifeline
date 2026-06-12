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
single-user, and needs **no extra dependencies for recall** by default (lexical) — the dense
semantic embedder is the only opt-in extra. Licensed **FSL-1.1-MIT** (source-available; converts to
MIT after two years).

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

<figure class="diagram-fig">
<svg class="diagram" viewBox="0 0 760 200" role="img" aria-label="The loop: read the assembled context on connect, propose entries while working">
<defs>
<linearGradient id="loopg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7c89ff"/><stop offset="1" stop-color="#41d6c3"/></linearGradient>
<marker id="lA" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#7c89ff"/></marker>
<marker id="lB" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#41d6c3"/></marker>
</defs>
<path d="M598 82 C 472 26, 290 26, 168 78" fill="none" stroke="url(#loopg)" stroke-width="2.5" marker-end="url(#lA)"/>
<text x="383" y="24" text-anchor="middle" fill="#8a8f98" font-size="13" font-family="'JetBrains Mono',monospace">① CONNECT — read the assembled context</text>
<path d="M168 122 C 290 176, 472 176, 598 120" fill="none" stroke="url(#loopg)" stroke-width="2.5" marker-end="url(#lB)"/>
<text x="383" y="192" text-anchor="middle" fill="#8a8f98" font-size="13" font-family="'JetBrains Mono',monospace">② WORK — propose · a human approves (HITL)</text>
<rect x="58" y="72" width="190" height="56" rx="13" fill="#0d0e10" stroke="#7c89ff" stroke-opacity=".5"/>
<text x="153" y="105" text-anchor="middle" fill="#f7f8f8" font-size="17" font-family="Inter,sans-serif" font-weight="600">Your AI</text>
<rect x="512" y="72" width="200" height="56" rx="13" fill="#0d0e10" stroke="#41d6c3" stroke-opacity=".5"/>
<text x="612" y="105" text-anchor="middle" fill="#f7f8f8" font-size="17" font-family="Inter,sans-serif" font-weight="600">Lifeline ledger</text>
</svg>
<figcaption>Read the assembled context on connect; propose entries while working — a human approves. Both sides, every session.</figcaption>
</figure>

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
