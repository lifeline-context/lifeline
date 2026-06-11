# Teams & hosted — the Lifeline hub (early access)

The open-source core is everything one person needs: a local ledger, the MCP server, recall, the loop.
The **hub** is the hosted layer that makes Lifeline work for a *team* without anyone running infra.

> **Status: early access.** The hub is deployed and the GitHub App + Marketplace billing are built and
> tested, but onboarding is hands-on while we shape it with the first teams. Want in? See
> [Request access](#request-access) below.

## Free vs hosted

| | **Core (free, OSS)** | **Hub (hosted, paid)** |
|---|---|---|
| License | FSL-1.1-MIT (self-host anything) | proprietary service |
| Ledger | local `.lifeline/`, or your own Supabase | managed, backed up |
| MCP server | run `lifeline-mcp` yourself | **zero-ops hosted endpoint** per line |
| Users | single-user | **team lines** — shared, multi-user, role-scoped |
| Auth | your own | hosted OAuth (Google/GitHub) |
| GitHub | — | **GitHub App**: capture decisions from PRs, anchored to the merge SHA |
| Billing | — | **GitHub Marketplace** (GitHub bills; you keep 95%) |

The free core never becomes a trial that expires — local Lifeline is yours under the FSL. The hub
charges for **not operating it yourself** plus the team features (shared lines, sync, backup, the App).

## What the hub adds, concretely

- **Hosted MCP, multi-tenant.** Point your AI at *your* endpoint; an OAuth token scopes it to your
  line by row-level security. No process to babysit.
- **Team lines.** A shared, append-only line your whole team reads and proposes into — same
  content-addressed entries, namespaced to the team, curated by line owners.
- **GitHub App.** Opt-in capture: a `/lifeline` comment or the `lifeline` label on a PR drafts a
  proposal from the human PR text (never the diff), anchored to the merge-commit SHA — Law 1 for free,
  without touching the entry id (Law 3).
- **Backup & sync.** The ledger is content-addressed, so backup/restore is lossless and idempotent.

The hub is a thin proprietary control-plane **around** the open core — it imports `lifeline-context`,
never forks it. Your reasoning stays portable: export anytime, re-seed anywhere, same ids.

## Request access {#request-access}

- **Star / watch** the repo to track the launch: [github.com/lifeline-context/lifeline](https://github.com/lifeline-context/lifeline)
- **Tell us about your team** — open a GitHub issue tagged `hosted` with your team size and what you'd
  put in a shared line. That shapes the early-access cohort.
- Curious what the control-plane looks like? There's a live (early, bare) dashboard — ask in the issue
  and we'll point you at it.

Not ready for a team yet? Start solo with the free core — [Getting started](getting-started.html) — and
graduate the same ledger to a hosted line later. Nothing to migrate; the entries are already portable.
