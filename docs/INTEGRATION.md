# Integration — closing the loop without a human

Lifeline has two sides, and the AI drives both:

- **Read on connect** → MCP resource `lifeline://project/context` (or `python -m lifeline context`).
- **Write while working** → MCP tools `lifeline_append` / `lifeline_recontextualize` (or `python -m lifeline log`).

## MCP client (any of them)

Point the client at the stdio server. The server command is **`lifeline-mcp`** (installed by
`pip install lifeline-context`); it reads the DB from `LIFELINE_DB` (default `.lifeline/ledger.db`).
Set the env var the way your client config does — e.g. an `"env"` block in the JSON snippets below.
At a shell directly:

```bash
LIFELINE_DB=.lifeline/ledger.db lifeline-mcp        # bash/zsh
```
```powershell
$env:LIFELINE_DB=".lifeline/ledger.db"; lifeline-mcp    # PowerShell
```

- **Resource:** `lifeline://project/context` — read it when opening the session.
- **Tools:** `lifeline_append(kind, summary, body, …)`, `lifeline_recontextualize(parent_id, summary, body, …)`, `lifeline_recall(query, …)`.
- **Server command:** `lifeline-mcp` (or `python -m lifeline.mcp_server` from the repo root).
- **Named line:** set `LIFELINE_LINE=<name>` instead of `LIFELINE_DB` — the server derives
  `.lifeline/<name>.db` (an explicit `LIFELINE_DB` always wins).

## Per-client snippets (copy-and-paste)

**Claude Code** — already reads the project's `.mcp.json` **automatically**. Without it: `claude mcp add lifeline -- lifeline-mcp`.

**Cursor** — `.cursor/mcp.json` (at the project root):
```json
{ "mcpServers": { "lifeline": { "command": "lifeline-mcp", "env": { "LIFELINE_DB": ".lifeline/ledger.db" } } } }
```

**Claude Desktop** — `claude_desktop_config.json` (use an ABSOLUTE path — the cwd differs):
```json
{ "mcpServers": { "lifeline": { "command": "lifeline-mcp", "env": { "LIFELINE_DB": "C:/path/to/project/.lifeline/ledger.db" } } } }
```

**Gemini CLI** — `~/.gemini/settings.json`:
```json
{ "mcpServers": { "lifeline": { "command": "lifeline-mcp", "env": { "LIFELINE_DB": ".lifeline/ledger.db" } } } }
```

> WEB chat apps (claude.ai, ChatGPT) do **not** belong here — they require a remote server + OAuth
> (see `docs/MCP_REMOTE.md`). These snippets are for dev/CLI/IDE clients (stdio, local).

**Verification status (honest):** Claude Code (stdio, `.mcp.json`, named lines) and the remote
path (claude.ai connector via OAuth RS mode: 401 without a token, 200 with a valid JWT, consent
page) are **validated live** on this very repo. The Cursor / Claude Desktop / Gemini CLI snippets
follow each client's documented config format but haven't been exercised end-to-end by us yet —
if you run one, [tell us what happened](https://github.com/lifeline-context/lifeline/issues/new)
(works-fine reports are as valuable as bugs).

## Capture while you work (close the loop automatically)

- **Local, zero-LLM:** `lifeline capture` drafts proposals from your recent **git commit
  messages** (the commit body is the *why*; commits without one are skipped). Run it at the end
  of a work session; curate with `lifeline review`.
- **Team, on GitHub:** the Lifeline GitHub App drafts proposals from every **merged PR**'s
  human-written text (description + reviews) into the hub's Review queue — edit, approve or
  reject there. Opt-in per repo; PRs with no written rationale are skipped silently.

## Auto-connect in Claude Code (SessionStart hook)

Inject the context at the start of each session via the project's `.claude/settings.json`
(the hook's stdout enters the context). Example — adjust to your version's hook schema:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python -m lifeline context" } ] }
    ]
  }
}
```

Without a hook, the minimal convention (in CLAUDE.md) is: **on opening, run `python -m lifeline context`
and read it before acting.** When making any decision/feature/fix, append — that way the next AI
(or you tomorrow) connects and already knows.
