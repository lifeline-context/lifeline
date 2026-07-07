"""Ingester: lê uma LIFELINE.md (markdown) e carrega os entries no ledger (store).

Lossless: preserva ts e parents quando presentes. Para markdown no formato antigo
(prev_hash, sem campo `parents`) encadeia linearmente (single-writer). Para markdown
GERADO pelo store (com `parents` e `id` explícitos) reconstrói o DAG exato — base do
round-trip estável que torna o store a fonte de verdade e a markdown uma projeção.
"""
import logging
import re
from datetime import datetime
from typing import Dict, List

from lifeline.entry import Entry
from lifeline.projection import BODY_END
from lifeline.store import EventStore

_log = logging.getLogger("lifeline.ingest")


def _parse_ts(s: str):
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _blocks(text: str) -> List[str]:
    """Fatia o markdown em blocos-de-entrada. Formato NOVO (com a sentinela BODY_END): corta
    por ela — robusto a `### #`/`---` DENTRO do body (gap #G6). Formato LEGADO (sem sentinela):
    cai no fatiamento por `^### #` (compatível com markdowns antigas)."""
    if BODY_END in text:
        out = []
        for seg in text.split(BODY_END):
            i = seg.find("### #")
            if i != -1:
                out.append(seg[i:])
        return out
    return ["### #" + part for part in re.split(r"(?m)^### #", text)[1:]]


def parse_markdown(text: str) -> List[Dict]:
    legacy = BODY_END not in text
    out = []
    for block in _blocks(text):
        header = re.match(r"### #(\d+)\s+—\s+(\S+)\s+—\s+(\w+)", block)
        if not header:
            continue

        def field(name):
            m = re.search(rf"(?m)^- \*\*{name}\*\*:\s*(.*)$", block)
            return m.group(1).strip() if m else ""

        bm = re.search(r"\*\*Body\*\*:\s*\n(.*)", block, re.S)
        # Formato novo: o corpo é tudo até a sentinela (já removida pelo split) → só .strip()
        # (que casa com o `body.strip()` do hash, Lei #3). Legado: mantém o antigo corte de `---`.
        if bm:
            body = bm.group(1)
            if legacy:
                body = re.sub(r"\n*---\s*$", "", body)
            body = body.strip()
        else:
            body = ""

        parents_raw = field("parents")
        parents = ([] if parents_raw in ("", "—", "-")
                   else [p.strip() for p in parents_raw.split(",") if p.strip()])

        out.append({
            "ts": header.group(2),
            "kind": header.group(3),
            "author": field("author"),
            "agent": field("agent") or "human",
            "provider": field("provider") or "none",
            "model": field("model") or "human",
            "summary": field("summary"),
            "body": body,
            "parents": parents,
            # No formato NOVO (gerado pelo store) o campo `parents` é a verdade EXPLÍCITA —
            # inclusive vazio ("—" = root legítimo). No legado, vazio = "não sei" (encadeia).
            "explicit_parents": not legacy,
            "recorded_id": field("id") or field("hash"),
        })
    return out


async def ingest_text(text: str, store: EventStore, strict: bool = False) -> int:
    """Ingere o markdown no store. Anti-adulteração: quando a view registra um `id`
    (`recorded_id`), ele é COMPARADO ao id recomputado do conteúdo — uma view editada à
    mão re-hashearia silenciosamente para um id novo e o `verify` passaria sem acusar
    nada (buraco da auditoria). Mismatch: AVISA por padrão; `strict=True` falha.
    """
    prev_id = None
    count = 0
    mismatches = []
    for d in parse_markdown(text):
        if d["explicit_parents"]:
            # formato novo: `parents` é verdade explícita — [] é um ROOT legítimo (não
            # encadeia no prev_id; encadear mudaria o id e quebraria o round-trip/promote).
            parents = d["parents"]
        else:
            parents = d["parents"] if d["parents"] else ([prev_id] if prev_id else [])
        kwargs = dict(
            kind=d["kind"], author=d["author"], agent=d["agent"],
            provider=d["provider"], model=d["model"],
            summary=d["summary"], body=d["body"], parents=parents,
        )
        ts = _parse_ts(d["ts"])
        if ts is not None:
            kwargs["ts"] = ts
        entry = Entry(**kwargs)
        if d["recorded_id"] and d["recorded_id"] != entry.id:
            mismatches.append((d["recorded_id"], entry.id))
        if await store.append(entry):
            count += 1
        prev_id = entry.id
    if mismatches:
        detail = "; ".join(f"recorded {a[:12]}… != computed {b[:12]}…" for a, b in mismatches[:5])
        msg = (f"{len(mismatches)} entr{'y' if len(mismatches) == 1 else 'ies'} whose recorded id "
               f"doesn't match the recomputed content ({detail}) — the view was hand-edited, "
               f"corrupted, or written by a different hash scheme.")
        if strict:
            raise ValueError(msg)
        _log.warning("%s Ingested with RECOMPUTED ids (content wins over the recorded id).", msg)
    return count


async def ingest_markdown(path: str, store: EventStore, strict: bool = False) -> int:
    # newline="" → lê os bytes VERBATIM (sem universal-newlines). Espelha o write byte-fiel de
    # `_write_view`: o par write/read é a INVERSA exata um do outro, então o body volta com os
    # mesmos bytes (inclusive "\r\n" interno) e o id content-addressed se reproduz. Com
    # `read_text` (universal-newlines) um "\r\r\n" legado colapsava p/ "\n\n" (dobra), mudando
    # o body e quebrando o `verify` no rebuild.
    with open(path, encoding="utf-8", newline="") as f:
        return await ingest_text(f.read(), store, strict=strict)
