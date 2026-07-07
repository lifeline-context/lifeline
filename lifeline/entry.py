"""O Entry — a unidade atômica da linha de vida.

Content-addressed e determinístico (Lei #3): `id = sha256(conteúdo + pais)`.
`ts` e `dedup_key` são metadados e ficam FORA do hash, para que o mesmo conteúdo
gere o mesmo id em qualquer máquina ou momento — pré-requisito para dedup e merge
entre nós/usuários no futuro.
"""
import hashlib
from datetime import datetime, timezone
from typing import List, Literal, Optional, get_args

from pydantic import BaseModel, Field, model_validator

GENESIS = hashlib.sha256(b"GENESIS").hexdigest()

Kind = Literal[
    "bootstrap", "decision", "feature", "fix",
    "incident", "milestone", "release", "note", "open", "correction"
]

KINDS = get_args(Kind)  # tupla dos kinds válidos — usada pra validar propostas (anti-sujeira)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Entry(BaseModel):
    """Um registro imutável da cadeia de raciocínio do projeto."""

    model_config = {"strict": True}

    id: str = ""                                   # derivado (content-addressed)
    ts: datetime = Field(default_factory=utcnow)   # metadado — FORA do hash
    kind: Kind
    author: str
    agent: str = "human"
    provider: str = "none"
    model: str = "human"
    summary: str                                   # o *quê* (≤200 por convenção)
    body: str = ""                                 # o *porquê* (pesa mais)
    parents: List[str] = Field(default_factory=list)
    dedup_key: Optional[str] = None                # idempotência — FORA do hash

    def _canonical(self) -> str:
        """Deterministic canonical form — INJECTIVE by construction.

        Every field (and every parent) is encoded as `<utf8-byte-length>:<value>\\n`, then
        concatenated. The explicit length makes each field boundary unambiguous: no value can
        shift content into a neighbouring field, so two distinct Entries can never share a
        canonical form (the old `"\\n".join(fields)` was ambiguous — a `\\n` INSIDE a field
        moved the boundary and provably collided two different Entries into one id).
        Parents are sorted → the id is invariant to parent order. The leading `v2` versions
        the scheme so any future change gets its own, non-overlapping id space.
        """
        parts = [
            self.kind, self.author, self.agent, self.provider,
            self.model, self.summary, self.body.strip(),
            *sorted(self.parents),
        ]
        return "v2\n" + "".join(f"{len(p.encode('utf-8'))}:{p}\n" for p in parts)

    def compute_id(self) -> str:
        return hashlib.sha256(self._canonical().encode("utf-8")).hexdigest()

    @model_validator(mode="after")
    def _seal(self) -> "Entry":
        # Sela o id a partir do conteúdo+pais, se ainda não veio do storage.
        if not self.id:
            self.id = self.compute_id()
        return self

    def verify(self) -> bool:
        """True se o id ainda bate com o conteúdo (não foi adulterado)."""
        return self.id == self.compute_id()
