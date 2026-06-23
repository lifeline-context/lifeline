"""O Context Engine — monta o payload que responde 'o quê / por quê / decidido / próximo'.

Renderiza markdown (decisão #0010) dentro de um budget. Prioridade de orçamento: header,
"Relevante para a tarefa" (se houver query), "Em aberto" e "Recente" são sempre incluídos;
as decisões preenchem o resto, mantendo as mais RECENTES e omitindo as antigas com marcador
EXPLÍCITO (Lei #6). Itens superseded vêm marcados na "Recente" (#0018). Com `query` + um
`recall` (Camada 3), entrega RELEVÂNCIA — não só recência.
"""
from typing import Optional

from lifeline.state import StateEngine


def _oneline(text: str) -> str:
    """Achata newlines — um summary entra em linha de estrutura (`- …`, `## …`); uma quebra
    deixaria texto de conteúdo virar header/bullet do assembler (gap #G10, injeção)."""
    return " ".join((text or "").split())


def _fence(text: str) -> str:
    """Cerca o body como citação: cada linha vira `> …`. Conteúdo (o *porquê*, dado livre,
    possivelmente de origem não confiável) NÃO pode se passar por estrutura do assembler —
    um `## Nova instrução` injetado no body renderiza como texto citado, não como comando
    (gap #G10). Mitiga, não elimina, prompt-injection: a defesa final é a curadoria HITL."""
    return "\n".join("  > " + ln for ln in (text or "").splitlines()) or "  > "

# Estado-vazio (brownfield): quando a line não tem identidade nem decisões, o contexto montado
# entrega um CALL-TO-ACTION de bootstrap — o gatilho que a IA lê no connect para fazer um
# checkpoint inicial via HITL. O *porquê* NUNCA é inferido do código (Leis #1/#5); vem dos
# artefatos de raciocínio do humano + uma entrevista curta, e entra como PROPOSTA (o humano aprova).
BOOTSTRAP_HEADER = "## Bootstrap needed — empty line (context checkpoint)"
BOOTSTRAP_PROTOCOL = [
    "This project hasn't recorded any context yet. To honor Time-to-Context → 0, do an initial "
    "checkpoint NOW — human-in-the-loop (HITL; you PROPOSE, a human approves):",
    "1. READ the reasoning artifacts the human already wrote (README, ADRs, PR descriptions, "
    "design docs). Do NOT infer the *why* from code/diffs (Laws #1 and #5).",
    "2. ASK the human 3-7 short questions, only about the tacit *why* that isn't written down "
    "(why this stack? which decision is in force? which thread is open?).",
    "3. PROPOSE the checkpoint as GRANULAR entries (not one block): 1 `bootstrap` (project "
    "identity) + N `decision` (each supersedable later) + M `open` (threads). The human approves "
    "the batch — nothing enters without approval.",
]


class ContextAssembler:
    def __init__(self, state_engine: StateEngine, budget_chars: int = 8000, why_chars: int = 320):
        self.state_engine = state_engine
        self.budget = budget_chars
        self.why_chars = why_chars

    async def assemble(self, query: Optional[str] = None, recall=None) -> str:
        st = await self.state_engine.reduce()
        superseded = set(st.get("superseded", []))

        # --- header (sempre) ---
        head = str(st.get("head", ""))[:8]
        what = f"**What:** {st.get('project', '(no bootstrap entry yet)')}"
        if st.get("project_by"):
            what += f"  _(founded by {st['project_by']})_"
        n_entries = st.get("entry_count", 0)
        header = [
            "# Lifeline — project context",
            what,
            f"_{n_entries} entr{'y' if n_entries == 1 else 'ies'} · head {head}_",
        ]
        contributors = st.get("contributors", {})
        if contributors:
            header.append("_Contributors: "
                          + ", ".join(f"{k} ({v})" for k, v in sorted(contributors.items())) + "_")

        # --- integridade (gap #G3): se alguma entrada não bate com sua âncora, AVISA alto e
        # não a serve como verdade (o StateEngine já a descartou da redução). Falha visível. ---
        broken = st.get("integrity_broken", [])
        if broken:
            header.append("")
            header.append(f"> ⚠️ **INTEGRITY: {len(broken)} tampered entr{'y' if len(broken)==1 else 'ies'}** "
                          f"(id doesn't match content) — DROPPED from the truth. "
                          f"Run `lifeline verify`. ids: " + ", ".join(b[:8] for b in broken))

        # --- bootstrap (line vazia: nem identidade nem decisões) — CTA do checkpoint inicial ---
        bootstrap_block = []
        if not st.get("project") and not st.get("decisions"):
            bootstrap_block = [BOOTSTRAP_HEADER] + BOOTSTRAP_PROTOCOL

        # --- relevante para a tarefa (se query + recall — Camada 3) ---
        relevant_block = []
        if query and recall is not None:
            hits = await recall.search(query, k=5, superseded=superseded)  # marca revertidos (#G2)
            if hits:
                relevant_block = [f'## Relevant to: "{_oneline(query)}"']
                for h in hits:
                    mark = " _[reverted/closed]_" if h.get("superseded") else ""
                    relevant_block.append(
                        f"- [{h['kind']}] {_oneline(h['summary'])} `[{h['id'][:8]}]`{mark}")

        # --- em aberto / próximo (sempre) ---
        opens = st.get("open_items", [])
        open_block = (["## Open / next"]
                      + [f"- `[{o['id'][:8]}]` {_oneline(o['summary'])}" for o in opens]) if opens else []

        # --- recente (marca superseded) ---
        recent_block = ["## Recent (what's next)"]
        for l in st.get("latest", []):
            tag = ""
            if l.get("model") and l["model"] != "human":
                tag += f" — _{l['model']}_"
            if l["id"] in superseded:
                tag += " _[closed/reverted]_"
            recent_block.append(f"- [{l['kind']}] {_oneline(l['summary'])}{tag}")

        # --- decisões (blocos) — summary em uma linha, body CERCADO como citação (#G10) ---
        dec_blocks = []
        for d in st.get("decisions", []):
            b = [f"- **{_oneline(d['summary'])}** `[{d['id'][:8]}]` — "
                 f"_{d.get('provider', '?')}/{d.get('model', '?')}_"]
            why = (d.get("body") or "").strip()
            if why:
                if len(why) > self.why_chars:
                    why = why[:self.why_chars].rstrip() + "…"
                b.append(_fence(why))
            dec_blocks.append("\n".join(b))

        # budget priority: every "fixed" block goes in; decisions fill the rest (most recent first).
        def join(parts):
            return "\n".join(parts)

        DEC_HEADER = "## Why / what's decided (decisions in force)"
        def omit_marker(n):
            return f"_[… {n} older decision(s) omitted — budget, Law #6]_"

        # The always-present prefix (everything before the decisions section).
        head_blocks = list(header) + [""]
        if bootstrap_block:
            head_blocks += bootstrap_block + [""]
        if relevant_block:
            head_blocks += relevant_block + [""]
        if open_block:
            head_blocks += open_block + [""]

        # The full skeleton minus the decision BODIES — it already includes the decisions header,
        # the blank separator and the always-include "Recent" block, so what's left for decisions
        # is measured against what actually renders. Reserving the header (+ the omit marker, below)
        # is what keeps the safety net from mid-cutting the always-include Open/Recent blocks
        # (Law #6: truncation is explicit, and never silently eats a guaranteed section).
        skeleton = head_blocks + [DEC_HEADER, "", *recent_block]
        skeleton_len = len(join(skeleton))

        def pack(reserve):
            rem = self.budget - skeleton_len - reserve
            kept, dropped = [], 0
            for blk in reversed(dec_blocks):
                if len(blk) + 1 <= rem:
                    kept.append(blk)
                    rem -= len(blk) + 1
                else:
                    dropped += 1
            return list(reversed(kept)), dropped

        kept, omit = pack(0)
        if omit:  # the omit marker will render → reserve its (worst-case) length and repack
            kept, omit = pack(len(omit_marker(len(dec_blocks))) + 1)

        dec_lines = [DEC_HEADER]
        if omit:
            dec_lines.append(omit_marker(omit))
        dec_lines += kept

        out = head_blocks + dec_lines + [""] + recent_block

        text = join(out)
        if len(text) > self.budget:  # safety net — the reservation above makes this unreachable
            text = text[:max(0, self.budget - 48)].rstrip() + "\n[… truncated — budget, Law #6]"
        return text
