---
slug: hermes-agent-lifeline
title: "Give Hermes Agent a memory it can trust: Lifeline over MCP"
description: "Hermes Agent recalls what happened; it doesn't anchor why. Here's how Lifeline plugs in over MCP to give a self-improving agent a verifiable why layer."
keywords: "Hermes Agent, Nous Research, agent memory, MCP, Model Context Protocol, self-improving agent, anchored memory, AI agent context, decision amnesia"
date: 2026-06-10
author: jessianmart
faq:
  - q: "What is Hermes Agent?"
    a: "Hermes Agent by Nous Research is an open-source, self-improving AI agent that runs in the terminal, IDEs, and chat platforms. It builds skills from experience, calls 70+ tools, is model-agnostic, and is MCP-native — positioned alongside Claude Code and Codex."
  - q: "Does Lifeline replace Hermes Agent's memory?"
    a: "No. Hermes's native memory (curated MEMORY.md, FTS5 session search, LLM-summarized recall, Honcho user modeling) handles recall of what happened. Lifeline adds a different layer: an anchored, append-only record of why — decisions, rejected alternatives, and constraints — that the recall layer doesn't provide. They are complementary; Hermes executes, Lifeline remembers why."
  - q: "How do you connect Lifeline to Hermes Agent?"
    a: "Because Hermes is MCP-native, you register Lifeline as an MCP server — interactively with `hermes mcp`, or in `~/.hermes/config.yaml` under `mcp_servers` (a `command:` entry for the local stdio server, or a `url:` for a hosted endpoint). Lifeline then appears as a toolset the agent reads its anchored context from and proposes entries to."
  - q: "Why does a self-improving agent need anchored memory?"
    a: "A self-improving agent turns experience into skills and refines them. If its memory surfaces a reverted decision as current, or a summary distorts the original reasoning, the agent can crystallize the mistake into a skill and then improve that skill — amplifying a wrong lesson. Anchoring and supersession prevent that by marking what is current versus reverted, tied to immutable source events."
---

# Give Hermes Agent a memory it can trust: Lifeline over MCP

**[Hermes Agent](https://github.com/nousresearch/hermes-agent) by Nous Research is a self-improving AI agent — it builds skills from experience, runs across terminal, IDE, and chat, and connects to any model and any MCP server. What it recalls well, it doesn't yet *anchor*.** Lifeline plugs into Hermes over MCP to add exactly that: a verifiable, append-only memory of *why*.

This isn't a pitch to replace anything in Hermes. It's about the one layer a self-improving agent needs most and is hardest to build well — and why it belongs *outside* the agent.

## What Hermes Agent is — and what its memory does

Hermes is an *execution* runtime in the lineage of Claude Code and Codex: a central registry of 70+ tools across ~28 toolsets, programmatic tool calling that can collapse multi-step pipelines into a single inference, isolated subagents for parallel work, a cron scheduler, and delivery across Telegram, Discord, Slack, and more. It is **model-agnostic** by design — `hermes model` switches between Nous Portal, OpenRouter, OpenAI, or a custom endpoint with "no code changes, no lock-in" — and it is **MCP-native**, so any Model Context Protocol server becomes a toolset.

Its memory is multi-layered and built for **recall**: agent-curated `MEMORY.md`, FTS5 full-text session search, LLM summarization for cross-session recall, and Honcho-backed user modeling. For a conversational, multi-platform assistant, that is the right design — find what was said, summarize what happened, surface the relevant past.

## The gap: recall is not a trustworthy *why*

Recall and *anchored reasoning* are different problems. Call the gap **decision amnesia**: the agent can recall the *text* of a past decision and still lose its *why* — and whether it still holds. Three properties Hermes's native memory does not aim to provide:

- **Provenance.** FTS5 and LLM summaries surface *text*, not claims tied to the immutable event that produced them. A summary can drift from what actually happened, and the recall layer isn't designed to flag the drift.
- **Supersession.** `MEMORY.md` and session recall *accumulate*. They don't mark a decision as **reverted** — a rejected approach stays searchable as if it were still in force.
- **Currency over similarity.** Full-text search ranks by match, not by what is true *now*.

For most assistants this is tolerable. For a **self-improving** agent, it is the dangerous part.

## The self-improving trap

Here is the non-obvious risk, and it is specific to agents like Hermes. Hermes turns experience into skills and **improves them in use**. Now compound that with un-anchored memory.

If the agent's recall surfaces a *reverted* decision as relevant — or an LLM summary subtly rewrites *why* something was done — the agent doesn't merely repeat the mistake once. It can **crystallize it into a skill, and then improve that skill**, amplifying a wrong lesson with every cycle. A self-improving loop without anchored truth doesn't just forget; it **learns the wrong thing, confidently, and gets better at it.**

There's a second edge to this. Hermes is built to be *efficient* about reasoning: programmatic tool calling collapses multi-step pipelines into single inferences, and complex tasks crystallize into reusable skills. That efficiency is exactly what buries the *why* — the rationale gets compiled into a skill or a code path, not written where the next cycle (or the next model) can read it. **The better an agent gets at *doing*, the more invisible *why it did it* becomes.** The cure is not a smarter summarizer; it is an anchor — a record where every claim is tied to its source, and where a correction *supersedes* rather than blends into the past.

## How Lifeline plugs in — over MCP, no fork

Because Hermes is MCP-native, you register Lifeline the way you register any MCP server — interactively with `hermes mcp`, or directly in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  lifeline:
    command: lifeline-mcp        # local stdio server (pip install lifeline-context)
    # or, for a hosted endpoint (use instead of command):
    # url: https://<your-lifeline-host>/mcp
    # auth: oauth
```

Now, *alongside* Hermes's recall, the agent has a second memory surface that is:

- **Append-only and content-addressed** — the same reasoning yields the same identifier anywhere, so the record is deterministic and portable.
- **Anchored** — every entry carries the immutable identifier of the event that produced it, so claims are *checkable against their source*: the agent can verify rather than guess.
- **Superseding, not overwriting** — a correction references what it replaces, so a reverted decision is *visibly dead*, not silently searchable.
- **Human-in-the-loop** — the agent **proposes** entries; a person approves them, so the record stays signal instead of accumulating machine-generated drift.

The division is clean: Lifeline records the **why** — the decision, the alternative you rejected, the constraint that forced it. Hermes already has the **what** — the code, the tool calls, the trajectory. They don't overlap, and Lifeline deliberately does *not* try to be an agent runtime. Hermes executes; Lifeline remembers why.

## Why the *why* belongs outside the agent

Three of Hermes's strengths are exactly the ones that fragment an in-agent memory — and exactly where an external, anchored, provider-neutral record pays off:

- **Model switches.** Run `hermes model` to move from Nous Portal to OpenRouter mid-project and Hermes's `MEMORY.md` follows — but an LLM-summarized note was written in the prior model's voice and judgment. A content-addressed entry is byte-identical no matter which model writes or reads it, so the *why* doesn't quietly re-interpret when you switch.
- **Isolated subagents.** Hermes spins up isolated subagents for parallel work; each keeping its own scratch memory is exactly how two of them end up undoing each other. One shared anchored ledger gives every subagent the same source of truth to read and propose into.
- **Multi-platform.** A decision made in Hermes's terminal is the same one its Telegram or Discord session inherits, because it lives in a record both connect to over MCP — not in either session's scrollback.

Put in one line: this raises the agent's **share of context** — the portion of what Hermes reasons from that is your verified record rather than similarity-ranked guesswork.

## The community is already asking for this

An open issue on Nous's tracker [requests exposing Hermes memory (`MEMORY.md`/`USER.md`) via an MCP server](https://github.com/nousresearch/hermes-agent/issues/10835). The instinct is right: memory should be addressable over MCP, not trapped in a file. Lifeline is that surface — but anchored and curated, rather than a markdown log served raw. It is the same idea, taken to where a self-improving agent actually needs it.

## Before and after

**Before.** A week into a project, Hermes re-proposes an integration it had abandoned — the abandonment lived in a session summary that ranked low against the current query. It may scaffold a skill around the dead path.

**After.** Hermes reads Lifeline, sees the integration was chosen *and superseded and why*, routes around it, and proposes the newer rationale as an entry for you to approve. The reverted path stays dead; the agent's next cycle starts from what is actually true.

## Key takeaways

- Hermes Agent's native memory is built for **recall** (MEMORY.md, FTS5 search, LLM summaries, Honcho). It is not built for **anchored, superseding provenance** — and doesn't claim to be.
- For a **self-improving** agent, un-anchored memory is uniquely risky: it can turn a reverted decision into a refined skill, and the agent's own efficiency (programmatic tool calls, skills) buries the *why*.
- Lifeline plugs in over MCP (`hermes mcp` / `~/.hermes/config.yaml`) as a complementary **why layer**: append-only, content-addressed, anchored, superseding, human-curated.
- Because both are provider-neutral, the *why* survives model switches, subagents, and platforms — raising the agent's share of context.

## Frequently asked questions

**What is Hermes Agent?**
Hermes Agent by Nous Research is an open-source, self-improving AI agent that runs in the terminal, IDEs, and chat platforms. It builds skills from experience, calls 70+ tools, is model-agnostic, and is MCP-native — positioned alongside Claude Code and Codex.

**Does Lifeline replace Hermes Agent's memory?**
No. Hermes's native memory (curated MEMORY.md, FTS5 session search, LLM-summarized recall, Honcho user modeling) handles recall of what happened. Lifeline adds a different layer: an anchored, append-only record of why — decisions, rejected alternatives, and constraints — that the recall layer doesn't provide. They are complementary; Hermes executes, Lifeline remembers why.

**How do you connect Lifeline to Hermes Agent?**
Because Hermes is MCP-native, you register Lifeline as an MCP server — interactively with `hermes mcp`, or in `~/.hermes/config.yaml` under `mcp_servers` (a `command:` entry for the local stdio server, or a `url:` for a hosted endpoint). Lifeline then appears as a toolset the agent reads its anchored context from and proposes entries to.

**Why does a self-improving agent need anchored memory?**
A self-improving agent turns experience into skills and refines them. If its memory surfaces a reverted decision as current, or a summary distorts the original reasoning, the agent can crystallize the mistake into a skill and then improve that skill — amplifying a wrong lesson. Anchoring and supersession prevent that by marking what is current versus reverted, tied to immutable source events.

> **Give your agent a memory it can verify** — open source, no signup:
>
> ```
> pip install lifeline-context
> # then register `lifeline-mcp` under mcp_servers in ~/.hermes/config.yaml
> ```

---

*Related reading: [Share of context](/blog/share-of-context.html) · [How AIs inherit each other's context](/blog/ai-context-handoff.html) · [Context engineering](/blog/context-engineering.html). [Lifeline](https://github.com/lifeline-context/lifeline) is an open-source context runtime — git for reasoning, MCP-native and provider-agnostic. Hermes Agent is a trademark of Nous Research; this is an independent integration write-up.*
