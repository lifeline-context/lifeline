# Changelog

All notable changes are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/); this project is **beta** (pre-1.0), so minor
versions may still break.

## [Unreleased]

## [0.5.0] — 2026-07-07

> **BREAKING — hash scheme v2.** A line-by-line audit proved the v1 canonical form was **not
> injective**: a `\n` inside any field could collide two *different* entries into the same id —
> the exact anti-hallucination anchor the product stands on. v2 length-prefixes every field, so
> distinct content can never share an id. **Existing ledgers must run `lifeline rehash` once**
> (topological old→new remap; automatic `.bak` backup; verify enforced before/after). Views
> regenerate with the new ids; `migrate --strict` proves a clean round-trip.

### Fixed
- **Content-addressing is now injective (Law #1/#3)** — the audited collision
  (`agent="b\nc"` vs `body="f\ng"`) is closed and locked by property tests.
- **Lines are now first-class end-to-end** (the audit found four holes):
  - `LIFELINE_LINE` now works for the **local** MCP server too (it was a silent no-op outside
    the cloud — the server always opened `LIFELINE_DB`); precedence: explicit `LIFELINE_DB` >
    `LIFELINE_LINE` > default.
  - Cloud HITL queue is **line-scoped** on `get`/`set_status` (an approve/reject by pid could
    reach a *different line* of the same owner).
  - `lifeline clone` rebuilds (and verifies) **every** cloned line, not just the default.
  - `lifeline lines` now works against the cloud store as well.
- **Text→store integrity**: ingest validates the recorded id against the recomputed content —
  a hand-edited view now warns (or fails with `migrate --strict`) instead of silently
  re-hashing; generated views with explicit empty `parents` round-trip as true roots.
- **`lifeline push` stages surgically** (`LIFELINE*.md` only) — it no longer runs `git add -A`,
  which could sweep unrelated WIP (or worse, secrets) into a "lifeline: sync" commit.
- **`pull`/`clone` verify after merging** — a merge that breaks the DAG now reports BROKEN
  instead of returning success.

### Added
- **`lifeline promote --from <line> --to <line> --id …|--kind …`** — copy entries across
  parallel lines as roots, with provenance notes; idempotent by content-addressing
  (re-promoting dedups; superseded entries are skipped with `--kind`).
- **`lifeline rehash`** — one-shot migration for hash-scheme upgrades.
- **`lifeline capture`** — zero-LLM local capture: drafts proposals from recent **git commit
  messages** (conventional prefix → kind; the commit body is the *why* — commits without one
  are skipped, honest abstention). Idempotent via a `capture.head` marker; everything lands
  **PENDING** in the HITL queue, never directly on the line.
- **`lifeline exam`** — Context Health 0–100: integrity **gates** the score (a broken chain is
  0/F), then identity, why-density, direction, freshness, and a TTC probe (does the assembled
  context answer what/why/decided/next?). Every gap is paired with the command that fixes it;
  `--json` for CI.
- Git subprocess decoding pinned to **UTF-8** — on Windows, a commit body with non-codepage
  characters (e.g. `✓`) crashed `capture`/sync via the locale decoder.

### Changed
- Dense-recall embeddings are **cached by entry id** (content-addressed → the cache can never
  go stale); indexing is incremental instead of re-embedding the whole ledger per query.
- Supersession fixpoint gained a defensive iteration cap (a cyclic correction graph can no
  longer hang `reduce()`).
- Removed the dead `/auth/v1/user` introspection verifier (JWKS superseded it in #0049).

## [0.4.0] — 2026-06-23

### Fixed
- **Lossless round-trip through disk** (#0084): `_write_view`/`ingest_markdown` are byte-faithful
  (`newline=""`), and `.gitattributes` pins `LIFELINE.*` as `-text` so git never re-normalizes the
  content-addressed view (a CRLF body no longer breaks `verify` after `migrate`).
- **Budget no longer truncates the "Recent" block**: the assembler now reserves the decisions
  header + omission marker in its budget math, so the always-include "Open / next" and "Recent"
  sections survive small budgets instead of being cut by the safety net (Law #6).

### Changed
- **Tool & server output is now English** across the assembled context, the CLI, and the MCP
  surface (the *why* an AI reads). Portuguese docs remain bilingual.
- **Authorization Server hardened** (#0086): hosted social login via Supabase (drops the dev-only
  password grant from the production path), an optional **persistent DCR client store**
  (`lifeline_oauth_clients`) so registered connectors survive restarts/replicas, and a
  `redirect_uri` allow-list check at `/authorize` (rejects URIs the client never registered).

### Added
- **Server branding over MCP** (#0091, SEP-973): the server advertises its icon + website via
  `serverInfo.icons`/`websiteUrl` on `initialize`, so compliant clients show the Lifeline mark.
- **Concurrency proof**: tests assert idempotency under concurrent identical appends (exactly one
  entry inserted) and union-without-duplicates when two divergent views merge into one store.

### Packaging
- Pin `mcp>=1.20` (the `Icon`/`website_url` API and the JWKS/multipart transitive deps the server
  imports). The `[remote]` extra is now self-sufficient — `PyJWT[crypto]`, `python-multipart`, and
  `starlette` are declared, so `pip install lifeline-context[remote]` runs the hosted server as-is.
- The OAuth **consent page ships inside the wheel** (`lifeline/templates/consent.html`), loaded via
  `importlib.resources` — the hosted AS no longer 404s on a `pip install`.

## [0.3.0] — 2026-06-10

### Changed
- **License → [FSL-1.1-MIT](LICENSE)** (Functional Source License): source-available — free for any
  non-competing use, **converts to MIT two years** after each release. The paid layer is the hosted
  **hub**, not the code. Versions **≤ 0.2.0 stay MIT** (already published).

### Fixed — gap audit (silent-failure hardening)
- **#G1** prefix-resolution for parent ids: the MCP only ever hands an AI a *truncated* id, so
  `recontextualize`/`log` now expand the prefix to the full id (and refuse orphan/ambiguous) —
  before, supersession was a silent no-op.
- **#G3** read-time anchor verify: `StateEngine.reduce` verifies each entry and drops tampered
  content from the truth (the assembler flags it) instead of serving it.
- **#G4** `verify` detects omission (dangling parents); the reducer no longer trusts `seq` alone.
- **#G8** supersession is reversible (fixpoint over the correction graph) — reverting a reversion
  restores the original.
- **#G5** per-embedder abstention floor (dense recall no longer admits noise).
- **#G6** lossless round-trip via a body sentinel (bodies containing `### #` or trailing `---` no
  longer corrupt on clone/pull).
- **#G7** `approve` honors dedup (no false "approved"); **#G10** entry bodies are fenced as quotes
  in the payload (prompt-injection mitigation).

### Added — hosted-connector auth (#0049, #0079)
- **Resource Server** validating the Bearer JWT by **JWKS (ES256)** offline (`SupabaseJWKSVerifier`).
- Adopted Supabase's **native OAuth 2.1 Server** (DCR + auth-code/PKCE) as the recommended hosted
  path; a self-contained **custom Authorization Server** (`lifeline/oauth.py`, `LIFELINE_OAUTH_AS=1`)
  remains as a fallback. A static **consent page** ships in `site/oauth/consent/`.
- Deploy robustness: the remote server **announces its mode** at boot and warns instead of silently
  falling back to authless; public URL / allowed-hosts **auto-derive on Render**; `SUPABASE_URL`
  and `ALLOWED_HOSTS` are normalized; Supabase failures degrade gracefully (no bare 500s).

## [0.2.0] — 2026-06-01

### Added
- **Dense semantic recall (#0029):** `SentenceTransformerEmbedder` behind the existing `Embedder`
  port — recall by **meaning**, not keywords. **Opt-in** (`pip install lifeline-context[embeddings]`);
  select with `LIFELINE_EMBEDDER=dense` (env) or `make_embedder(...)`. The default stays
  `LexicalEmbedder` (zero-dependency). Wired into `lifeline context --query` and the MCP `lifeline_recall`.

## [0.1.1] — 2026-06-01

### Added
- `lifeline schema` — prints the bundled Supabase schema; the schema now **ships in the package**
  (`lifeline/schema.sql`), so `pip install` users get it without cloning the repo.
- OSS hygiene: `SECURITY.md`, this `CHANGELOG.md`, and GitHub issue/PR templates.

### Tests
- Integration tests for the CLI `main()` dispatch (+ the friendly error path) and the MCP read
  handlers (`project_context`/`recall`). Coverage 80% → 84% (core stays 100%).

## [0.1.0] — 2026-06-01

First public release. 🧬

### Added
- **Local core (100% test coverage):** content-addressed, append-only ledger (`Entry`,
  `SQLiteEventStore`); state reduction via reducers (`StateEngine`, status as a projection);
  budget-aware context assembly (`ContextAssembler`); anchored lexical recall (`SemanticRecall`);
  store↔markdown projection with a proven fixed-point round-trip.
- **CLI** (`lifeline`): `log`, `propose`/`review`/`approve`/`reject` (HITL curation), `context`
  (`--query`/`--budget`), `verify`, `rebuild`, `migrate`, `lines`, `schema`, `push`/`pull`/`clone`
  (git sync, Tier 0); `--line` (named lines) and `--store {sqlite,supabase}`.
- **MCP** (`lifeline-mcp`): resource `lifeline://project/context` + tools `lifeline_append`,
  `lifeline_recontextualize`, `lifeline_recall`; built-in usage instructions so any connecting AI
  self-onboards. Per-client setup in `docs/INTEGRATION.md`.
- **Cloud (M3):** Supabase adapters (`SupabaseEventStore`, `SupabaseStagingStore`) — append-only
  RLS + a mutable HITL proposal queue; remote MCP server (`lifeline-mcp-remote`, HTTP/SSE) with an
  OAuth 2.1 **Resource Server** (multi-tenant by user JWT). Live-validated.
- Bilingual docs (EN + PT-BR), `.mcp.json`, `Dockerfile`, `render.yaml`, GitHub Actions CI, and
  PyPI publishing via OIDC Trusted Publishing.

### Known limits
- Recall is **lexical** (keyword), not dense-semantic — see issue/entry #0029.
- Hosted **web-chat** connectors (claude.ai/ChatGPT) require an OAuth Authorization Server (#0049);
  dev clients (Claude Code/Cursor/Gemini CLI) connect to the local OSS directly.
- No retry/backoff in the cloud adapter yet (errors are logged and raised).

The full *why* behind every decision lives in [`LIFELINE.md`](LIFELINE.md), starting at #0001.

[0.5.0]: https://github.com/lifeline-context/lifeline/releases/tag/v0.5.0
[0.4.0]: https://github.com/lifeline-context/lifeline/releases/tag/v0.4.0
[0.3.0]: https://github.com/lifeline-context/lifeline/releases/tag/v0.3.0
[0.2.0]: https://github.com/lifeline-context/lifeline/releases/tag/v0.2.0
[0.1.1]: https://github.com/lifeline-context/lifeline/releases/tag/v0.1.1
[0.1.0]: https://github.com/lifeline-context/lifeline/releases/tag/v0.1.0
