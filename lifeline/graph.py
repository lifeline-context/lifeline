"""Grafo tipado de entidades de projeto — uma PROJEÇÃO do ledger (Fase 1 do Regente).

Ainda é memória, não execução: registra que "o serviço A depende do B", não roda nada. Uma
relação é uma Entry `kind=relation` cujos `parents=[from, to]` (content-addressed; o `verify`
já garante que ambas as pontas existem — fecho referencial de graça) e cujo body declara a
DIREÇÃO. A direção mora no body porque no hash os `parents` são um conjunto ordenado (Lei #3):
a ordem não sobrevive, então `from`/`to` precisam ser explícitos.

Formato do body de uma relação:
    rel: depends_on
    from: <id completo>
    to: <id completo>
"""
import re
from typing import Any, Dict, List, Optional

from lifeline.entry import RELATION_TYPES
from lifeline.state import StateEngine
from lifeline.store import EventStore

_REL = re.compile(r"(?m)^rel:\s*(\S+)\s*$")
_FROM = re.compile(r"(?m)^from:\s*(\S+)\s*$")
_TO = re.compile(r"(?m)^to:\s*(\S+)\s*$")


def relation_body(rel: str, from_id: str, to_id: str) -> str:
    if rel not in RELATION_TYPES:
        raise ValueError(f"unknown relation '{rel}'. Use one of: {', '.join(RELATION_TYPES)}")
    return f"rel: {rel}\nfrom: {from_id}\nto: {to_id}"


def parse_relation(body: str) -> Optional[Dict[str, str]]:
    """{rel, from, to} de um body de relação, ou None se não casar o formato."""
    r, f, t = _REL.search(body or ""), _FROM.search(body or ""), _TO.search(body or "")
    if r and f and t and r.group(1) in RELATION_TYPES:
        return {"rel": r.group(1), "from": f.group(1), "to": t.group(1)}
    return None


class ProjectGraph:
    """Nós = entidades (qualquer Entry que não seja `relation`); arestas = relações EM VIGOR
    (as supersedidas por correction somem, igual às decisões)."""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}     # id → {kind, summary}
        self.edges: List[Dict[str, str]] = []          # {rel, from, to}

    @classmethod
    async def build(cls, store: EventStore) -> "ProjectGraph":
        superseded = set((await StateEngine(store).reduce()).get("superseded", []))
        g = cls()
        async for e in store.stream():
            if e.id in superseded:
                continue
            if e.kind == "relation":
                rel = parse_relation(e.body)
                # aresta só entra se as duas pontas são nós conhecidos e vivos
                if rel and rel["from"] not in superseded and rel["to"] not in superseded:
                    g.edges.append({**rel, "id": e.id})
            else:
                g.nodes[e.id] = {"kind": e.kind, "summary": e.summary}
        return g

    # ---- consultas (a resposta ESTRUTURADA, não texto) ----
    def _match(self, rel: Optional[str], key: str, value: str) -> List[Dict[str, str]]:
        return [ed for ed in self.edges
                if ed[key] == value and (rel is None or ed["rel"] == rel)]

    def outgoing(self, node_id: str, rel: Optional[str] = None) -> List[Dict[str, Any]]:
        """O que `node_id` aponta (ex.: rel=depends_on → do que ele depende)."""
        return [self._as_hit(ed["to"], ed) for ed in self._match(rel, "from", node_id)]

    def incoming(self, node_id: str, rel: Optional[str] = None) -> List[Dict[str, Any]]:
        """O que aponta para `node_id` (ex.: rel=depends_on → quem depende dele — dependents)."""
        return [self._as_hit(ed["from"], ed) for ed in self._match(rel, "to", node_id)]

    def _as_hit(self, node_id: str, edge: Dict[str, str]) -> Dict[str, Any]:
        n = self.nodes.get(node_id, {})
        return {"id": node_id, "rel": edge["rel"],
                "kind": n.get("kind", "?"), "summary": n.get("summary", "(unknown node)")}
