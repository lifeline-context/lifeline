# Concepts & laws

Lifeline is an **event-sourced reasoning ledger**. The "current truth" an AI reads is a *derived
projection* of an immutable, content-addressed event log — never the source itself.

## Entry — the atomic unit

Everything is an `Entry`, content-addressed:

```
id = sha256(kind, author, agent, provider, model, summary, body.strip(), sorted-parents)
```

`ts` (timestamp) and `dedup_key` stay **outside** the hash. Consequence: the **same content +
parents produce the same id on any machine, at any time** — the basis for dedup and sync (more
content-pure than git, whose commit sha includes the timestamp). `parents` is **sorted** in the
hash, so a merge of A+B equals B+A.

## The 3 memory layers

All anchored to the same immutable ledger:

- **Ledger (Layer 1)** — a hashed, append-only DAG. The source of truth. `append()` is idempotent:
  re-inserting the same id is silently ignored, which solves split-brain trivially.
- **State (Layer 2)** — pure reducers fold the stream into the current truth: identity, decisions
  in effect, open threads, recent, contributors. **Status is a projection, not a state machine.**
- **Recall (Layer 3)** — relevance search where every hit is **anchored** to its source event.
  Lexical (zero-dependency) by default; a dense semantic embedder is opt-in via the `[embeddings]`
  extra (`LIFELINE_EMBEDDER=dense`).

## Supersession

A `correction` entry referencing another entry's id removes it from the current truth — a reverted
decision, a closed thread. **Append-only:** the past is never edited; closing or reverting is always
a *new* entry.

## Lines — separate reasoning threads

A **line** is an independent, content-addressed ledger: its own DAG and its own generated view. A
project has one by default (`ledger` → `LIFELINE.md`) and adds more on demand — `--line <name>` on the
CLI, `LIFELINE_LINE` for the MCP server, or per-request on the hosted hub. Each maps to its own files
(`.lifeline/<name>.db` + `LIFELINE.<name>.md`) with **no collisions**; `lifeline lines` lists them.

Lines are **isolated** — there are no cross-line references. Use them to keep distinct *contexts*
apart instead of letting one stream blur them:

- **Audience / visibility** — this project runs a public `ledger` (engineering) next to a private
  `--line strategy` (`LIFELINE.strategy.md`: pricing, moat), so each *why* lives where it belongs.
- **Subsystem or experiment** — one line per service, spike, or A/B path: each thread stays
  self-contained and its view diffs on its own.
- **Branch of exploration** — give a candidate direction its own line. Ids are content-addressed, so
  promoting a branch's conclusion into another line is **idempotent** — the same entry can't double-insert.

### Branching *within* a line — the DAG

Inside one line, reasoning isn't flat: every entry carries `parents`. A **merge** entry
(`parents = [A, B]`) joins two sub-threads — and because parents are sorted in the hash, A+B ≡ B+A. A
**correction** *prunes* a branch: it supersedes its parents, so a rejected direction leaves the
current truth while staying in history — **anchored and visibly reverted**, never deleted.

<figure class="diagram-fig">
<svg class="diagram" viewBox="0 0 800 280" role="img" aria-label="A reasoning DAG inside one line: a branch is pruned by a correction; two branches merge">
<defs>
<marker id="dA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#7c89ff"/></marker>
<marker id="dM" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#41d6c3"/></marker>
<marker id="dP" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#5b606b"/></marker>
</defs>
<line x1="100" y1="143" x2="270" y2="68" stroke="#7c89ff" stroke-width="2" marker-end="url(#dA)"/>
<line x1="100" y1="145" x2="270" y2="145" stroke="#5b606b" stroke-width="2" stroke-dasharray="5 5" marker-end="url(#dP)"/>
<line x1="100" y1="147" x2="270" y2="222" stroke="#7c89ff" stroke-width="2" marker-end="url(#dA)"/>
<line x1="308" y1="66" x2="556" y2="136" stroke="#41d6c3" stroke-width="2" marker-end="url(#dM)"/>
<line x1="308" y1="224" x2="556" y2="154" stroke="#41d6c3" stroke-width="2" marker-end="url(#dM)"/>
<circle cx="80" cy="145" r="18" fill="#0d0e10" stroke="#7c89ff" stroke-width="2"/>
<circle cx="290" cy="62" r="18" fill="#0d0e10" stroke="#7c89ff" stroke-width="2"/>
<circle cx="290" cy="145" r="18" fill="#131417" stroke="#5b606b" stroke-width="2" stroke-dasharray="4 4"/>
<circle cx="290" cy="228" r="18" fill="#0d0e10" stroke="#7c89ff" stroke-width="2"/>
<circle cx="580" cy="145" r="22" fill="#0d0e10" stroke="#41d6c3" stroke-width="2.5"/>
<path d="M283 138 l14 14 M297 138 l-14 14" stroke="#5b606b" stroke-width="2"/>
<text x="80" y="184" text-anchor="middle" fill="#8a8f98" font-size="12.5" font-family="'JetBrains Mono',monospace">bootstrap</text>
<text x="290" y="34" text-anchor="middle" fill="#b7bdc6" font-size="12.5" font-family="'JetBrains Mono',monospace">decision A</text>
<text x="320" y="149" text-anchor="start" fill="#5b606b" font-size="12.5" font-family="'JetBrains Mono',monospace">B · superseded</text>
<text x="290" y="262" text-anchor="middle" fill="#b7bdc6" font-size="12.5" font-family="'JetBrains Mono',monospace">decision C</text>
<text x="580" y="190" text-anchor="middle" fill="#41d6c3" font-size="12.5" font-family="'JetBrains Mono',monospace">merge · parents [A,C]</text>
</svg>
<figcaption>Inside one line: a <strong>correction</strong> prunes decision B — superseded, gone from the current truth but still in history; A and C <strong>merge</strong>, and because parents are sorted, A+C ≡ C+A. Solid = in force · dashed = reverted.</figcaption>
</figure>

### Lines and Tree-of-Thoughts (ToT)

Lifeline is the **memory** a Tree-of-Thoughts writes to and reads from — it *records* the tree; it
does not run it (orchestrating agents is a non-goal — see below). Two clean mappings:

- **Branches as lines** — one line per candidate branch: fully isolated parallel exploration, each
  branch's *why* anchored. When one wins, you log its conclusion into the main line.
- **Branches within a line** — each thought is an entry whose `parents` point at the thought it
  extends; siblings off one parent are alternatives; a `correction` prunes the loser; a merge entry
  fuses the survivors.

The payoff is specific to ToT: its worst waste is **re-exploring an already-pruned branch** —
*decision amnesia* at the branch level. Because Lifeline keeps pruned branches *superseded, not gone*,
the next pass reads "this path was tried and rejected, and why," and routes around it instead of
redoing dead work.

## The anti-hallucination anchor

Every item the AI reads carries its source event's hash. **No anchor, no entry.** Getting a recall
match wrong cannot turn into a hallucination, because the vector is only an index — the truth is the
anchored event.

## The 7 laws (the constitution)

1. **No memory without an immutable anchor.** Every context item carries the hash of its source
   event. The anti-hallucination spine.
2. **Append-only.** Corrections are new entries referencing the prior id.
3. **Deterministic content-addressing.** Same content + parents → same id, on any node.
4. **Provider-agnostic storage; deliver in the provider's format.**
5. **The *why* outweighs the *what*.**
6. **Budget is first-class.** Context fits the window; truncation is always explicit, never silent.
7. **MCP-native.** The AI's interface is the product surface.

## Non-goals (what Lifeline is *not*)

Lifeline is **not** a cognitive OS, an MMU, an agent orchestrator/sandbox, a workflow engine, a git
replacement, an executor/curator (self-healing), or a trainer (fine-tuning). **It records
reasoning, not execution.** If an idea arrives dressed as a "hypervisor/microkernel/opcode," take
the costume off before evaluating it.
