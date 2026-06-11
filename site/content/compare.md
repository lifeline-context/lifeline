# Lifeline vs the alternatives — and when *not* to use it

Lifeline isn't trying to replace your docs, your wiki, or your memory tool. It occupies one narrow
slot most stacks leave empty: an **append-only, anchored record of *why*** the project is what it is,
served to any AI. Here's honestly where it sits next to the things it gets compared to — and where it
*isn't* the right tool.

## At a glance

| Tool | What it stores | Mutable? | Provenance / "still true?" | Machine-served | Lifeline's relationship |
|---|---|---|---|---|---|
| **Lifeline** | the project's *why* (decisions, reversals, incidents, open threads) | **append-only** | every item carries its event hash; corrections supersede | **MCP-native** | — |
| **ADRs** (markdown) | architecture decisions | edited in place | by convention only | no (just files) | ADRs *as a runtime* — anchored, AI-readable, supersession-aware |
| **CLAUDE.md / .cursorrules / AGENTS.md** | how the AI should *behave* (rules) | edited in place | none | read as instructions | **complementary** — rules ≠ rationale; this project ships both |
| **RAG over your repo** | code/text chunks by similarity | n/a (index) | none — ranks by match, not truth | yes | answers *where is X*; Lifeline answers *why X, and is it current* |
| **Memory MCPs** (mem0, Letta/MemGPT, Honcho) | agent/user memories, often vector-backed | auto-written, overwritten | usually none | yes | **complementary** — they recall; Lifeline *anchors* the why |
| **Wiki / Notion / Confluence** | human knowledge base | fully mutable | none | no | broader + human; Lifeline is narrower, tamper-evident, machine-native |
| **git** | the *what* (code), content-addressed by commit | append-only history | commit SHA | no | the *why* to git's *what*; **not** a git replacement (a non-goal) |

## The honest distinctions

- **vs ADRs** — the closest cousin. ADRs are a *doc convention*; Lifeline is a *runtime*. Same instinct
  (record the decision + the why), but content-addressed, served over MCP, **proposable by the AI**
  (human-approved), with supersession, relevance recall, and budgeted assembly. If you love ADRs,
  Lifeline is ADRs an AI can read, extend, and `verify` — that can't silently contradict themselves.
- **vs CLAUDE.md / rules files** — those say *how to act* ("always run tests"); Lifeline says *why the
  project is this way* ("Postgres, because the audit needs ACID `[hash]`"). Different jobs. Keep both.
- **vs RAG / vector search over code** — retrieval ranks text by similarity and has **no provenance**
  and no concept of *reverted*. Code shows *what*, never *why*. Lifeline anchors every claim to its
  source event and marks dead decisions dead — so a wrong match can't become a confident hallucination.
- **vs memory MCPs** — mem0/Letta/Honcho store mutable, auto-written memories (great for *recall* of
  what happened, user modeling, session continuity). Lifeline is **append-only + human-in-the-loop +
  content-addressed**: no silent overwrite, no machine-generated drift, every entry checkable against
  its origin. They're a recall layer; Lifeline is the anchored *why* layer. Run both.
- **vs git** — git is content-addressed *what*; Lifeline is content-addressed *why*. The `LIFELINE.md`
  even lives in git. Lifeline explicitly does **not** replace version control.

## When *not* to use Lifeline

Honesty is the brand, so:

- **A throwaway spike or solo one-off** with no future reader — the ceremony isn't worth it.
- **You won't curate it.** Writes are human-in-the-loop by design; a ledger nobody approves or
  supersedes **rots**, and a stale, confident ledger is *worse* than none. (See [Curate well](curate.html).)
- **You want an agent orchestrator, workflow engine, or execution memory** — those are explicit
  [non-goals](concepts.html). Lifeline records *reasoning*, it doesn't run anything.
- **You need to store code, secrets, or large blobs** — wrong tool; the body of an entry is *why* text.
- **A pure docs/marketing surface with no decisions** — there's nothing to anchor.

Lifeline pays off when a project has **ongoing decisions whose rationale future minds (AI or human)
must inherit**, and someone will spend thirty seconds approving the entries that matter.
