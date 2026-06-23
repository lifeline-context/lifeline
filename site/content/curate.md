# Curate well — keeping the ledger signal, not noise

Lifeline lives or dies on one thing: **the ledger stays true and dense.** Writes are human-in-the-loop
on purpose — the AI proposes, you approve — because a reasoning record that nobody curates **rots**,
and a stale, confident ledger is *worse* than no ledger: it misleads the next mind faster. This page
is the practice that keeps it worth reading.

## The five habits

1. **One entry per unit of work *with meaning*** — not per file, not per commit, not per tool call. A
   feature, a decision, a fix, an incident, a reversal. If it doesn't change what the next AI should
   believe, it's not an entry.
2. **The *why* is mandatory.** The body is the rationale, and write-time refuses an empty one (Law 5:
   the why outweighs the what). "Switched to Postgres" is noise. "Postgres over SQLite — the audit
   needs cross-row ACID and we'll outgrow a single writer" is signal.
3. **Capture the decision *and its rejected alternative.*** The gold is "we chose X over Y because Z."
   The road not taken is what stops the next agent from re-proposing Y next week.
4. **Supersede, never edit.** Reversed a decision? `lifeline log --kind correction --parents <id>`
   (or the `lifeline_recontextualize` tool) writes a *correction* that supersedes the old entry by id.
   The past stays in history, marked reverted — never silently rewritten (Laws 2 & 3).
5. **Be ruthless at approval.** The AI will over-propose. Reject the changelog-y ones. The ledger is a
   record of *reasoning*, not a diff of *activity* — git already has the activity.

## What a good entry looks like

```
GOOD  kind=decision
      summary: "Anchor captured entries to the merge SHA, not a new id"
      body:    "Law 1 needs an immutable anchor; Law 3 fixes id = sha256(content+parents).
                Putting the SHA *in* the id would break determinism, so it rides in a
                sidecar (hub_entry_sources). Rejected: a parents-based link (no external SHA)."

BAD   kind=note
      summary: "Updated github.py"
      body:    "refactored some functions"          # what, not why — git has this
```

## Ledger rot — the failure mode, named

The honest risk: entries pile up, a decision gets reversed in the code but not in the ledger, and
six weeks later a fresh AI reads a confident lie. Lifeline is **built to resist** this, but it can't do
it alone:

- **Append-only + supersession** mean a reverted decision is *visibly dead*, not quietly wrong — but
  only if you actually write the correction when you reverse.
- **`lifeline verify`** is tamper-evident: it proves the chain wasn't edited (it won't catch a *true
  entry you forgot to supersede* — that's the human's job).
- **Budget (Law 6)** truncates old decisions explicitly, so the window never silently drops context.

The anti-rot routine:

- **Append at the moment of the decision**, not in a Friday batch you'll forget.
- **Recontextualize the instant you reverse** — a dead decision left "in force" is the #1 rot source.
- **Read `lifeline context` as a stranger would**, periodically. If it's wrong, fix *forward* (a new
  entry), never by hand-editing `LIFELINE.md` (it regenerates from the store anyway).
- **Keep entries about *why*.** The repo, git, and your issue tracker already hold the *what*.

A well-curated Lifeline is small, dense, and current — a few hundred entries that a new mind reads in
seconds and trusts completely. That trust is the entire product; protect it.
