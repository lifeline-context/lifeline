---
slug: share-of-context
title: "Share of context: the metric behind Lifeline"
description: "Share of context is the portion of an AI's reasoning that comes from your curated, anchored record — the AI-era metric Lifeline is built to move."
keywords: "share of context, context engineering, generative engine optimization, MCP, AI-assisted development"
date: 2026-06-10
author: jessianmart
faq:
  - q: "What is share of context?"
    a: "Share of context is the portion of an AI's working context — on any task touching your project or domain — that comes from your curated, anchored record, rather than generic model priors, similarity-ranked retrieval, or someone else's framing. It is the AI-era successor to share of voice."
  - q: "How is share of context different from share of voice or GEO?"
    a: "Share of voice measures your slice of advertising impressions; GEO (generative engine optimization) is the practice of being cited by AI answer engines. Share of context is the underlying metric both point at: how much of what a model actually reasons from is yours. Unlike share of voice, it is a stock you accrue and own, not a flow you rent."
  - q: "How do you increase your share of context?"
    a: "Capture your reasoning (the why, not just the what), anchor every claim to its source so the model gets a trust signal, and deliver it to any AI on connect over a standard interface like MCP. That replaces the model's priors and similarity-ranked guesses with your curated record."
  - q: "Can you measure share of context?"
    a: "Roughly: open a fresh AI session on a real task and judge how much of what it knows is your specifics versus generic patterns — does it cite your actual decisions, and does it know what you reverted? The gap between what it reasons from and your real record is your unowned share."
---

# Share of context: the metric behind Lifeline

**Share of context is the portion of an AI's working context — on any task touching your project — that comes from your curated, anchored record, rather than generic model priors, similarity-ranked retrieval, or someone else's framing.** It is quietly becoming the metric that shapes what AI actually knows about your work. It is also the single idea Lifeline is built around.

## From share of voice to share of context

Every era of competition has had its share metric. Advertising had **share of voice** — your slice of category impressions. Retail had **share of shelf**; search had **share of search**. The pattern is always the same: identify the scarce channel between you and a decision, and measure how much of it is yours.

As AI moves from a novelty to the layer that mediates real work, the scarce channel shifts again. It is no longer the user's attention; it is the **model's working context** — the finite set of things a model actually reasons from when it acts. Your slice of that is your share of context.

The strategic turn is subtle but total: you used to compete to be *seen* by a person. Now you compete to be *in the context* a model reasons from. A model working on your problem will draw on something. The only question is how much of that something is yours.

## Why this share is different

Here is the part that makes share of context more than the next entry in the list. Every earlier share metric is a **flow you rent**: share of voice lasts exactly as long as you keep buying impressions — stop paying, and it is gone tomorrow. Share of context is a **stock you accrue and own**.

Once a decision and its *why* are captured and anchored, they do not expire when the campaign ends. They persist. They compound — the more of your reasoning a model can draw on, the more it defaults to your framing instead of its priors, which makes the next session start from a higher baseline. And because a good record is provider-agnostic, that stock travels with you across vendors and models instead of being trapped in one tool. You do not rent your way to share of context; you build it, and it keeps compounding.

## Two arenas, one metric

Share of context plays out in two places at once.

- **Inside your team — your AI on your codebase.** When an assistant works on your repo, its share of context is how much of the *why* comes from your record versus re-derivation and guesswork. Low share looks familiar: it re-proposes decisions you already settled and re-walks dead ends you already mapped. This is the world of [time-to-context](/blog/time-to-context.html), [context engineering](/blog/context-engineering.html), and [the handoff problem](/blog/ai-context-handoff.html) — those are the *mechanics*; share of context is the *scoreboard*.
- **Out in the world — any AI answering about your domain.** When someone asks an AI about your product, your company, or your category, how much of its answer is grounded in your authoritative material versus third parties and stale priors? That is what [generative engine optimization (GEO)](/docs/concepts.html) is really chasing.

Same metric, two scopes: the context your *own* AIs reason from, and the context the *world's* AIs reason from. Both are winnable, and both are usually left on the table.

## How you lose it

Share of context leaks in four predictable ways:

1. **Priors fill the gap.** Where your specifics are missing, the model substitutes generic training priors — plausible, confident, and not yours.
2. **Similarity beats truth.** Retrieval surfaces what looks relevant, including reverted approaches and competitor framing. Without anchoring, the model cannot tell live reasoning from dead reasoning.
3. **Ephemerality.** Your best reasoning happened in a chat or a PR thread and evaporated. The next model cannot draw on what no longer exists in a durable place.
4. **No trust signal.** Even when your context is present, if the model cannot tell current from stale, it discounts or misuses it.

Sum the leaks and most teams operate at a low share — losing ground they never knew was contested, because the metric was invisible.

## How Lifeline wins it

Lifeline is a context runtime: an append-only, content-addressed, **anchored** ledger of a project's *why*, served to any AI over MCP. Read through this lens, every part of it is a move to raise share of context:

- **It captures the why, not just the what** — so your reasoning is present in a durable place instead of evaporating into a transcript. (Plugs leak #3.)
- **It anchors every claim** to the immutable event that produced it, with corrections that supersede rather than overwrite — so the model gets a trust signal: this is current, that was reverted. (Plugs #2 and #4.)
- **It delivers on connect over [MCP](/docs/mcp.html)**, provider-agnostic — so every AI, any vendor, any session, reasons from your record instead of its priors. (Plugs #1, and makes the share portable rather than locked to one tool.)
- **It keeps a human in the loop.** The AI proposes entries; a person approves them. That keeps your share of context high-*quality*, not merely high-volume — signal, not noise.

The compounding result: in every session, a larger and more trustworthy slice of what the model reasons from is yours. You stop renting space in a model's defaults and start owning the context it stands on.

There is a fitting tell in how this very page reached you. Lifeline's site is engineered for external share of context too — anchored claims, structured data, an [llms.txt](/llms.txt) — so that when an AI is asked about context engineering, Lifeline's framing is in the context it answers from. The product and its go-to-market run on the same metric.

## Measuring your share of context

You can audit it in five minutes. Open a fresh AI session on a real task in your project and watch what it reasons from:

1. Is it citing *your* actual decisions, or inventing plausible ones?
2. Does it know what you tried and **reverted** — or does it re-propose it?
3. How much of its plan is your specifics versus generic best-practice patterns?

The distance between what the model reasons from and your real record is your unowned share. Much of it is recoverable — and recovering it is the work.

## Key takeaways

- **Share of context** is the portion of an AI's working context that comes from your curated, anchored record — the AI-era successor to share of voice and share of search.
- Unlike earlier share metrics, it is a stock you accrue and own, not a flow you rent: once captured and anchored, it persists, compounds, and travels across vendors.
- It leaks through priors, similarity-over-truth retrieval, ephemeral reasoning, and missing trust signals — inside your team and out in the world.
- Lifeline is built to win it: capture the *why*, anchor every claim, deliver to any AI over MCP, and keep a human curating — so a larger, more trustworthy slice of what AI reasons from is yours.

## Frequently asked questions

**What is share of context?**
Share of context is the portion of an AI's working context — on any task touching your project or domain — that comes from your curated, anchored record, rather than generic model priors, similarity-ranked retrieval, or someone else's framing. It is the AI-era successor to share of voice.

**How is share of context different from share of voice or GEO?**
Share of voice measures your slice of advertising impressions; GEO (generative engine optimization) is the practice of being cited by AI answer engines. Share of context is the underlying metric both point at: how much of what a model actually reasons from is yours. Unlike share of voice, it is a stock you accrue and own, not a flow you rent.

**How do you increase your share of context?**
Capture your reasoning (the why, not just the what), anchor every claim to its source so the model gets a trust signal, and deliver it to any AI on connect over a standard interface like MCP. That replaces the model's priors and similarity-ranked guesses with your curated record.

**Can you measure share of context?**
Roughly: open a fresh AI session on a real task and judge how much of what it knows is your specifics versus generic patterns — does it cite your actual decisions, and does it know what you reverted? The gap between what it reasons from and your real record is your unowned share.

> **Start owning your share of context** — open source, no signup:
>
> ```
> pip install lifeline-context
> python -m lifeline context
> ```

---

*Related reading: [Time-to-context](/blog/time-to-context.html) · [Context engineering](/blog/context-engineering.html) · [How AIs inherit each other's context](/blog/ai-context-handoff.html). [Lifeline](https://github.com/lifeline-context/lifeline) is an open-source context runtime — git for reasoning, MCP-native and provider-agnostic.*
