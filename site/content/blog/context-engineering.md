---
slug: context-engineering
title: "Context engineering: the discipline beyond prompt engineering"
description: "Prompt engineering shapes one request. Context engineering shapes what the model knows across every request — the discipline, and why it lasts."
keywords: "context engineering, prompt engineering, AI memory, decision log, anti-hallucination, MCP"
date: 2026-06-10
author: jessianmart
faq:
  - q: "What is context engineering?"
    a: "Context engineering is the practice of deliberately designing what an AI knows about a project — the durable, anchored record of decisions and reasoning it inherits — rather than optimizing a single prompt. Prompt engineering tunes one request; context engineering tunes the knowledge behind every request."
  - q: "How is context engineering different from prompt engineering?"
    a: "Prompt engineering shapes the wording of a single interaction and resets when the session ends. Context engineering builds a persistent, curated, verifiable base of project knowledge — the why behind decisions — that any model inherits on connect. One is per-message; the other is institutional."
  - q: "What is decision amnesia?"
    a: "Decision amnesia is the failure mode where every model, forever, re-proposes settled questions and re-walks rejected paths, because the reasoning never outlived the chat it happened in. It is the default state of a team without engineered context."
  - q: "Do better models make context engineering less necessary?"
    a: "No — they make it more valuable. As raw capability commoditizes across vendors, what a model produces on your codebase is bounded by the context it stands on, and a more capable model extracts more leverage from a clean, current why. Better models raise the ceiling; engineered context decides how much of it you reach."
---

# Context engineering: the discipline beyond prompt engineering

**Context engineering is the practice of deliberately designing what an AI knows about a project — not how a single prompt is worded.** Prompt engineering tunes one request and resets when the chat closes. Context engineering builds the durable, anchored knowledge that every request draws on, and that any new model inherits the moment it connects.

As AI moves from one-off chats to persistent collaborators on real codebases, the leverage shifts. The wording of a clever prompt matters less and less; the quality of the *context* a model stands on matters more and more.

## From per-message to institutional

Prompt engineering is real and useful — but it is **per-message**. You craft a careful instruction, you get a better answer, and then the session ends and the craft evaporates. The next session starts cold.

Context engineering operates one level up. Its unit is not the message; it's the **project's accumulated reasoning**, made portable across sessions, models, and teammates. The deliverable isn't a prompt. It's a base of knowledge a fresh mind can stand on without a human re-explaining it.

The two relate cleanly: [time-to-context](/blog/time-to-context.html) is the *metric* (how long until an AI can act correctly), and context engineering is the *discipline* that moves it.

None of this is wholly new. Senior teams have kept decision logs and Architecture Decision Records (ADRs) for years, for the same reason: a choice is worth more with its rationale attached. Context engineering takes that instinct and adapts it for the AI era — the record stops being a wiki page nobody reopens and becomes a machine-consumable, anchored substrate delivered to a model the moment it connects. Same instinct; a different consumer, and a much higher bar for being current and verifiable.

## Three principles of good context engineering

### 1. The *why* outweighs the *what*

Your repository already records the *what*: every line, every diff, every commit message. What it does not record is the *why* — the alternative you tried and abandoned, the constraint that forced an ugly-looking design, the decision you reverted and the reason.

Concretely: your team evaluates a message queue, rejects it because the operational cost isn't worth it at current volume, and writes that reasoning in a PR comment. The PR merges; the comment is now archaeology. Two sprints later, an AI surveys the architecture and helpfully proposes — a message queue. The *why* existed, but it wasn't a first-class artifact, so it didn't survive. Context engineering treats that *why* as deliberately as code: written at the moment of decision, in human language, where the next mind will actually read it.

### 2. Every claim is anchored

Institutional memory is only useful if it can be trusted. The failure mode of "just write down the context" is that notes drift, contradict the code, and quietly become a *second* source of hallucination.

The fix is **anchoring**: every item of context carries the immutable identifier of the event that produced it; a decision points to the change that enacted it, a correction points to the entry it supersedes. The model — and the human reviewing it — can verify rather than guess. In practice an entry looks like this:

```
decision  7a1f4d…  "Adopt the managed OAuth provider"
  why: a self-hosted auth server was more surface to secure and maintain than it
       earned; the managed provider covers our flows.
  supersedes  2c9e08…  "Build a custom authorization server"
```

Anyone — human or AI — can now see not just the current decision but the one it replaced, and why. Anchoring is what turns a pile of notes into a record you can build on.

### 3. Corrections are additive, never destructive

Reasoning evolves. You revert decisions; you change your mind for good reasons. Good context engineering never edits the past — it **appends a correction that references what it supersedes.** "What's true now" is computed from the chain, not by overwriting it. An AI then sees both the current decision *and* that an earlier one was reverted — exactly the signal that stops it from re-proposing the rejected path.

## The shape of an engineered context layer

Put the principles together and a practical structure emerges — three layers over one durable record:

- **A ledger** — an append-only, content-addressed log of reasoning events. Content-addressing means the same reasoning yields the same identifier on any machine, so the record is deterministic and portable.
- **State** — the current truth, computed by reducing the ledger: which decisions are in force, which were superseded, what's still open.
- **Recall** — anchored retrieval, so a model can ask "did we already decide something about X?" and get a trustworthy, cited answer.

This is the architecture behind [Lifeline](/docs/architecture.html): the reasoning record is the source of truth, the state is derived, and any AI reads the assembled result over [MCP](/docs/mcp.html). Crucially, the AI **proposes** entries and a human **approves** them — context engineering keeps a curator in the loop, so the record stays clean instead of accumulating machine-generated noise.

## Why better models make context engineering *more* valuable

The common assumption is that as models get smarter, you'll need less of this — that capability will absorb the missing context. The opposite holds.

Raw capability is **commoditizing**: every vendor's frontier model is broadly competent, so the model itself is no longer the differentiator. What a model produces on *your* codebase is bounded by the *context* it stands on — and a more capable model extracts *more* leverage from a clean, current *why* than a weak one does. Better models raise the ceiling; engineered context decides how much of that ceiling you actually reach. The smarter the model, the more a good context substrate is worth — which is precisely backwards from how most teams budget their attention today.

Skip the work and you get the default failure mode. **Decision amnesia** is the state where every model, forever, re-proposes settled questions and re-walks rejected paths, because the reasoning never outlived the chat it happened in. Teams that engineer their context hand every future model a running start; teams that don't pay full price for onboarding, indefinitely.

## Key takeaways

- **Context engineering** designs what an AI *knows* across every request; **prompt engineering** tunes a single request and resets.
- Its three principles: the *why* outweighs the *what*; every claim is anchored to an immutable source; corrections are additive, never destructive.
- A practical context layer is a ledger (append-only, content-addressed), derived state (current truth), and anchored recall — with a human curating what gets recorded.
- Better models make this *more* valuable, not less: as capability commoditizes, engineered context becomes the durable advantage. Skip it and you get decision amnesia.

> **See it for yourself** — open source, no signup:
>
> ```
> pip install lifeline-context
> python -m lifeline log --kind decision --summary "..." --body "...the why..."
> ```

## Frequently asked questions

**What is context engineering?**
Context engineering is the practice of deliberately designing what an AI knows about a project — the durable, anchored record of decisions and reasoning it inherits — rather than optimizing a single prompt. Prompt engineering tunes one request; context engineering tunes the knowledge behind every request.

**How is context engineering different from prompt engineering?**
Prompt engineering shapes the wording of a single interaction and resets when the session ends. Context engineering builds a persistent, curated, verifiable base of project knowledge — the why behind decisions — that any model inherits on connect. One is per-message; the other is institutional.

**What is decision amnesia?**
Decision amnesia is the failure mode where every model, forever, re-proposes settled questions and re-walks rejected paths, because the reasoning never outlived the chat it happened in. It is the default state of a team without engineered context.

**Do better models make context engineering less necessary?**
No — they make it more valuable. As raw capability commoditizes across vendors, what a model produces on your codebase is bounded by the context it stands on, and a more capable model extracts more leverage from a clean, current why. Better models raise the ceiling; engineered context decides how much of it you reach.

---

*Related reading: [Why time-to-context is the real bottleneck](/blog/time-to-context.html) · [How AIs inherit each other's context](/blog/ai-context-handoff.html). Lifeline is an open-source context runtime — git for reasoning.*
