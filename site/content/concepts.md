# Concepts & laws

Lifeline is an **event-sourced reasoning ledger**. The "current truth" an AI reads is a *derived
projection* of an immutable, content-addressed event log — never the source itself.

## Entry — the atomic unit

Everything is an `Entry`, content-addressed:

```
id = sha256(kind, author, agent, provider, model, summary, body, sorted-parents)
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
