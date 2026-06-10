---
slug: ai-context-handoff
title: "How one AI inherits another's context: solving the handoff problem"
description: "Two AIs on one project share nothing. Here's why the context handoff breaks — and how an anchored ledger over MCP makes context portable between models."
keywords: "AI context handoff, agent memory, multi-agent, cross-session AI, MCP, Model Context Protocol, shared AI memory, content-addressing, provider-agnostic, model lock-in"
date: 2026-06-10
author: jessianmart
faq:
  - q: "What is the AI context handoff problem?"
    a: "The context handoff problem is that when one AI's session ends — or when work passes to a different model, tool, or teammate's agent — the reasoning it built up is lost. The next AI starts from zero because context lives inside a transcript, not in a shared, portable record."
  - q: "What makes context portable between AI models?"
    a: "Four properties: the record is external to any session, provider-agnostic, content-addressed and anchored (so claims can be verified), and append-only with supersession (so corrections reference what they replace). With those, any model inherits any other's context on connect."
  - q: "How can one AI inherit another AI's context?"
    a: "By writing reasoning to a shared, provider-agnostic record instead of leaving it in a chat transcript. If each AI appends decisions to an append-only, content-addressed ledger and reads the assembled state over a standard interface like MCP, any other AI — regardless of vendor — inherits the same context on connect."
  - q: "Where does AI vendor lock-in actually live?"
    a: "Not in the model's weights — in the context trapped inside that vendor's sessions. Your switching cost to a better model is dominated by re-onboarding it on everything the old one knew. An external, provider-agnostic, anchored ledger inverts that: you keep the memory and swap the mind."
---

# How one AI inherits another's context: solving the handoff problem

**The context handoff problem is that reasoning built up by one AI is lost the moment work passes to another** — a new session, a different model, another tool, or a teammate's agent. Each one starts from zero, because the context lived inside a transcript instead of a shared, portable record.

As teams run more than one assistant — different vendors, different tools, agents working alongside agents — this becomes the defining interoperability problem of AI-assisted development.

## Three places handoff breaks

- **Across sessions (the same model, later).** Today's reasoning is in a chat you'll never reopen. Tomorrow's session inherits none of it, and re-derives or contradicts yesterday's conclusions.
- **Across models (different vendors).** Switch assistants and the new one has no access to the old one's history. The hard-won *why* doesn't travel. It dies with the transcript.
- **Across agents (working in parallel).** One agent decides to drop a dependency; a teammate's agent, an hour later on the same repo, re-adds it — because neither can see the other's reasoning. Two AIs, one project, zero shared memory, and often two conflicting directions.

In each case the same thing is missing: a place to put reasoning that is **outside** any single session and readable by **any** mind that connects.

## Why a shared context window isn't the answer

The tempting answer is "let them share a window" or "pass the transcript along." Neither makes context portable.

- **Context windows are per-session and per-model.** They are working memory, not a durable store. They vanish when the session ends and aren't designed to transfer across vendors.
- **Transcripts are the wrong unit, and the wrong size.** A raw conversation is mostly noise around a few decisions. Handing the next agent a 50,000-token chat log to "catch up" buries the three things it needed under everything it didn't — where reading an assembled current state might be a few hundred tokens of exactly the decisions still in force. Bigger is not the goal; *distilled and current* is.
- **There's no trust signal.** Even if you pass the text along, the receiving agent can't tell a current decision from an abandoned one. Without anchoring, inherited context is just a richer source of confident mistakes.

Handoff isn't a memory-size problem. It's a **shared-record-and-trust** problem.

## What makes context portable between minds

For one AI to reliably inherit another's context, the record has to satisfy four properties:

1. **External to any session.** Reasoning is written to a durable store, not left in a transcript. The store outlives every chat.
2. **Provider-agnostic.** The store doesn't care which vendor wrote an entry or which reads it. Storage is neutral; delivery happens in whatever format the connecting model expects.
3. **Content-addressed and anchored.** Each entry's identity is derived from its content, so the same reasoning yields the same identifier anywhere, and every claim is tied to the immutable event that produced it. The inheriting agent can verify, not guess.
4. **Append-only with supersession.** New conclusions don't overwrite old ones; corrections reference what they replace. The receiving agent sees both the current decision and the fact that an earlier one was reverted — the exact signal that prevents it from re-walking a dead end.

Put differently: stop handing the next AI a *conversation*, and start handing it a *curated, verifiable state*.

## The handoff in practice

One assistant, mid-project, decides to drop a half-built custom authorization server in favor of a managed OAuth provider, and records it:

```
decision  7a1f4d…  "Adopt the managed OAuth provider"
  why: the self-hosted auth server was more attack surface and upkeep than it earned.
  supersedes  2c9e08…  "Build a custom authorization server"
```

A week later a *different* model — different vendor, different session, maybe a teammate's agent — connects to the same project over MCP. It reads the assembled current truth, sees that a custom auth server was started *and deliberately abandoned and why*, and does not re-propose building one. The handoff happened with no human re-explaining anything. That is context inherited, not re-derived.

## Your real lock-in is the context, not the model

Here's the strategic turn most teams miss. Your lock-in to an AI vendor doesn't live in the model's weights — it lives in the **context trapped inside that vendor's sessions.** The moment a better model ships, your switching cost is dominated by re-onboarding it on everything the old one knew: the decisions, the dead ends, the constraints. That's the real exit tax.

An external, provider-agnostic, anchored ledger inverts it. Because any model can inherit the same context on connect, switching models becomes cheap — you keep the memory and swap the mind. Vendor-neutral context isn't just an interoperability nicety; it's the only durable defense against model lock-in. In a market where the best model changes every few months, owning your context — not renting it inside one vendor's chat history — is the position you want.

This is what a context runtime like Lifeline is for. Each AI **proposes** reasoning entries (a human approves them), which are appended to a content-addressed, anchored ledger; any other AI reads the assembled current truth over [MCP](/docs/mcp.html). See [the architecture](/docs/architecture.html) and [the underlying concepts](/docs/concepts.html). Because the ledger is provider-agnostic and content-addressed, a decision written by one model is inherited identically by the next.

## Key takeaways

- The **context handoff problem** is that reasoning is lost whenever work passes to another session, model, or agent — because it lived in a transcript, not a shared record.
- Shared context windows don't solve it: they're per-session, per-model, noisy, and carry no trust signal.
- Portable context requires a record that is external to any session, provider-agnostic, content-addressed and anchored, and append-only with supersession.
- Your real AI lock-in is the context trapped in a vendor's sessions — an external, anchored, vendor-neutral ledger is what makes models swappable.

> **Make context portable in two commands** — open source, no signup, vendor-neutral:
>
> ```
> pip install lifeline-context
> python -m lifeline context
> ```

## Frequently asked questions

**What is the AI context handoff problem?**
The context handoff problem is that when one AI's session ends — or when work passes to a different model, tool, or teammate's agent — the reasoning it built up is lost. The next AI starts from zero because context lives inside a transcript, not in a shared, portable record.

**What makes context portable between AI models?**
Four properties: the record is external to any session, provider-agnostic, content-addressed and anchored (so claims can be verified), and append-only with supersession (so corrections reference what they replace). With those, any model inherits any other's context on connect.

**How can one AI inherit another AI's context?**
By writing reasoning to a shared, provider-agnostic record instead of leaving it in a chat transcript. If each AI appends decisions to an append-only, content-addressed ledger and reads the assembled state over a standard interface like MCP, any other AI — regardless of vendor — inherits the same context on connect.

**Where does AI vendor lock-in actually live?**
Not in the model's weights — in the context trapped inside that vendor's sessions. Your switching cost to a better model is dominated by re-onboarding it on everything the old one knew. An external, provider-agnostic, anchored ledger inverts that: you keep the memory and swap the mind.

---

*Related reading: [What context engineering is](/blog/context-engineering.html) · [Why time-to-context is the real bottleneck](/blog/time-to-context.html). Lifeline is an open-source context runtime — git for reasoning, MCP-native and provider-agnostic.*
