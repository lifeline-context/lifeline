# Changelog

All notable changes are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/); this project is **alpha** (pre-1.0), so minor
versions may break.

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

[0.1.0]: https://github.com/jessianmart/lifeline/releases/tag/v0.1.0
