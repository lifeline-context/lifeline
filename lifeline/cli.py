"""CLI do Lifeline — o store é a fonte de verdade; a LIFELINE.md é uma view gerada.

    lifeline init                                           # projeto em andamento: mostra o protocolo de bootstrap (checkpoint HITL)
    lifeline log --kind decision --summary "…" --body "…"   # humano: anexa direto (você é o aprovador)
    lifeline propose --kind … --summary … --body …          # propõe (HITL) — entra pendente, não na line
    lifeline review                                         # lista pendências (curadoria)
    lifeline approve <pid|all> | reject <pid|all>           # HITL: sela ou descarta
    lifeline context [--query "…"] | verify | rebuild | migrate --from … | lines

Tiering (como aprovar comando shell): humano no `log` = commit direto; IA via MCP = `propose`
(pendente até um humano aprovar). Multi-line: `--line <nome>` → .lifeline/<nome>.db + LIFELINE.<nome>.md.
"""
import argparse
import asyncio
import glob
import json
import os
import re
import shutil
import sys

from lifeline import sync
from lifeline.entry import Entry, KINDS
from lifeline.store import SQLiteEventStore, resolve_parents
from lifeline.staging import SQLiteStagingStore
from lifeline.ingest import ingest_markdown, _parse_ts
from lifeline.projection import render_ledger_markdown
from lifeline.state import StateEngine
from lifeline.context import ContextAssembler, BOOTSTRAP_HEADER, BOOTSTRAP_PROTOCOL

DEFAULT_DB = os.environ.get("LIFELINE_DB", os.path.join(".lifeline", "ledger.db"))
DEFAULT_OUT = "LIFELINE.md"
LINES_DIR = ".lifeline"

# Store ativo, escolhido por main() via --store (default: SQLite local). Fica aqui para o
# seam _open() trocar de adapter sem reescrever cada comando. Resetado a cada main().
_STORE = {"kind": "sqlite", "line": "ledger"}
# Comandos que só fazem sentido no store local (git e glob de .db). O HITL
# (propose/review/approve/reject) já funciona na nuvem via SupabaseStagingStore.
_LOCAL_ONLY = {"push", "pull", "clone", "rehash", "promote", "capture"}

PREAMBLE = """# LIFELINE — lifeline

> An append-only chain of *whys*. The project records *why* it is what it is, and any mind that
> connects inherits that why instantly — with no one re-explaining.
>
> **This file is GENERATED** from the ledger (in `.lifeline/`), which is the source of truth.
> Do NOT hand-edit — append with `lifeline log` and it regenerates.
>
> **Start at #0001.** It's the whole project in human language.

## Protocol

1. **Append-only.** Never edit entries; a correction is a new entry (`kind: correction`) that
   references in `parents` the `id` it corrects — superseding it in the current truth.
2. **One entry per unit of work with meaning.** Not per file, not per tool call. The *why*
   outweighs the *what* (Law #5).
3. **Content-addressed identity (Law #3):** `id = sha256(kind, author, agent, provider, model,
   summary, body, sorted-parents)`. `ts` and `dedup_key` stay OUT of the hash — the same content
   yields the same `id` on any machine. `parents` form the causal DAG; there is no prev_hash (the
   ledger is a graph, not a list).
4. **Integrity:** `lifeline verify` checks that every `id` matches its content.
5. **Append:** `lifeline log --kind … --summary … --body …`. To see the assembled context an AI
   would receive: `lifeline context`.

## Project laws (the constitution)

1. **No memory without an immutable anchor.** Every context item carries the hash of its source
   event. The anti-hallucination spine.
2. **Append-only.** Corrections are new entries referencing the prior id.
3. **Deterministic content-addressing.** Same content + parents → same id, on any node.
4. **Provider-agnostic storage; deliver in the provider's format.**
5. **The *why* outweighs the *what*.**
6. **Budget is first-class.** Context fits the window; truncation is explicit, never silent.
7. **MCP-native.** The AI's interface is the product surface, not an appendix.

**Non-goals (law by omission):** Lifeline is NOT a cognitive OS, NOT an MMU, NOT an agent
orchestrator/sandbox, NOT a workflow engine, does NOT replace git, is NOT an executor/curator
(self-healing) or a trainer (fine-tuning/DL). It records reasoning.

---"""


def resolve_paths(line, db, out):
    """Resolve (db, out) a partir de --line (açúcar) ou dos flags explícitos.
    `--line NAME` mapeia ledger E view juntos, sem colisão entre lines."""
    if line:
        return os.path.join(LINES_DIR, f"{line}.db"), f"LIFELINE.{line}.md"
    return db, out


async def _open(db):
    if _STORE["kind"] == "supabase":
        from lifeline.cloud import SupabaseEventStore  # lazy: só puxa httpx no modo nuvem
        s = SupabaseEventStore(line=_STORE["line"])     # lê SUPABASE_URL/KEY do ambiente
        await s.initialize()
        return s
    os.makedirs(os.path.dirname(db) or ".", exist_ok=True)
    s = SQLiteEventStore(db)
    await s.initialize()
    return s


def _staging(db):
    """Fila HITL no backend ativo (espelha _open). Nuvem usa SupabaseStagingStore."""
    if _STORE["kind"] == "supabase":
        from lifeline.cloud import SupabaseStagingStore
        return SupabaseStagingStore(line=_STORE["line"])
    os.makedirs(os.path.dirname(db) or ".", exist_ok=True)
    return SQLiteStagingStore(db)


async def _head_id(store):
    last = None
    async for e in store.stream():
        last = e
    return last.id if last else None


async def _write_view(store, out):
    md = await render_ledger_markdown(store, PREAMBLE)
    # newline="" → escreve os bytes VERBATIM, sem traduzir "\n"→os.linesep (CRLF no Windows).
    # A tradução do modo-texto entrelaça o conteúdo com o fim-de-linha da plataforma: um body
    # com "\r\n" virava "\r\r\n" no arquivo e, na releitura (universal newlines), "\n\n" —
    # mudando os bytes do body e portanto o id content-addressed (Lei #3), o que quebrava o
    # `verify` após `migrate --from LIFELINE.md`. A projeção tem de ser determinística e
    # idêntica em qualquer SO; o pino em .gitattributes (-text) impede o git de re-mexer.
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(md)
    n = 0
    async for _ in store.stream():
        n += 1
    return n


def _validate(kind, body):
    """Anti-sujeira no write-time: kind válido + o *porquê* presente (Lei #5)."""
    if kind not in KINDS:
        raise ValueError(f"invalid kind '{kind}'. Use one of: {', '.join(KINDS)}")
    if not (body and body.strip()):
        raise ValueError("missing the *why* in --body (Law #5: the why weighs more than the what).")


async def cmd_log(db, out, kind, summary, body, author, agent, provider, model, parents):
    store = await _open(db)
    if parents is None:
        head = await _head_id(store)
        parents = [head] if head else []
    else:
        parents = await resolve_parents(store, parents)  # expande prefixos / recusa órfão (#G1)
    e = Entry(kind=kind, author=author, agent=agent, provider=provider,
              model=model, summary=summary, body=body or "", parents=parents)
    inserted = await store.append(e)
    n = await _write_view(store, out)
    return e, inserted, n


async def cmd_propose(db, kind, summary, body, author, agent, provider, model, parents):
    """Enfileira uma proposta (HITL). Async/leve: não toca na line, não regenera a view."""
    _validate(kind, body)
    staging = _staging(db)
    await staging.initialize()
    return await staging.propose(kind=kind, summary=summary, body=body, author=author,
                                 agent=agent, provider=provider, model=model, parents=parents)


async def cmd_review(db):
    staging = _staging(db)
    await staging.initialize()
    return await staging.pending()


async def cmd_approve(db, out, pids):
    staging = _staging(db)
    await staging.initialize()
    store = await _open(db)
    targets = await staging.pending() if pids == ["all"] else [await staging.get(int(p)) for p in pids]
    approved, duplicates, errors = 0, 0, []
    for prop in targets:
        if not prop or prop["status"] != "pending":
            continue
        head = await _head_id(store)
        stored = json.loads(prop["parents"]) if prop.get("parents") else []
        try:
            # expande prefixos / recusa parent órfão ANTES de selar (#G1): a IA via MCP só
            # conhece ids truncadas; sem isto a correção viraria no-op silencioso.
            stored = await resolve_parents(store, stored)
        except ValueError as ex:
            errors.append((prop["pid"], str(ex)))   # deixa PENDENTE; reporta, não sela
            continue
        parents = stored or ([head] if head else [])
        kw = dict(kind=prop["kind"], author=prop["author"], agent=prop["agent"],
                  provider=prop["provider"], model=prop["model"], summary=prop["summary"],
                  body=prop["body"] or "", parents=parents)
        ts = _parse_ts(prop["ts"])           # preserva o momento da decisão (capture-at-start)
        if ts is not None:
            kw["ts"] = ts
        inserted = await store.append(Entry(**kw))   # #G7: honra o retorno (dedup ≠ aprovado)
        if inserted:
            await staging.set_status(prop["pid"], "approved")
            approved += 1
        else:
            await staging.set_status(prop["pid"], "duplicate")
            duplicates += 1
    n = await _write_view(store, out) if approved else 0
    return approved, n, duplicates, errors


async def cmd_reject(db, pids):
    staging = _staging(db)
    await staging.initialize()
    ids = [p["pid"] for p in await staging.pending()] if pids == ["all"] else [int(p) for p in pids]
    for pid in ids:
        await staging.set_status(pid, "rejected")
    return len(ids)


async def cmd_rebuild(db, out):
    store = await _open(db)
    return await _write_view(store, out)


async def cmd_verify(db):
    """Integridade do ledger. Checa DUAS coisas (#G3/#G4):
    (1) conteúdo — todo id bate com seu conteúdo (anti-adulteração, Lei #1);
    (2) fecho referencial — todo `parent` citado existe no store (anti-OMISSÃO: deletar uma
        entrada do meio deixa filhos com pai fantasma; o `verify` antigo não via o buraco).
    Limite declarado: `ts` está fora do hash (Lei #3) — adulteração de relógio não é coberta."""
    store = await _open(db)
    entries = [e async for e in store.stream()]
    ids = {e.id for e in entries}
    tampered = [e.id for e in entries if not e.verify()]
    dangling = [(e.id, p) for e in entries for p in e.parents if p not in ids]
    ok = not tampered and not dangling
    return ok, len(entries), tampered, dangling


async def cmd_migrate(src, db, strict=False):
    store = await _open(db)
    return await ingest_markdown(src, store, strict=strict)


async def cmd_rehash(db, out):
    """Recomputa TODO id sob o esquema canônico ATUAL (Lei #3), remapeando parents old→new em
    ordem topológica (seq) num store novo. Migração one-shot para upgrades do canônico (ex.:
    v1→v2 injetivo): ids "tampered" são ESPERADOS aqui — é exatamente o que o rehash conserta.
    Recusa só dano ESTRUTURAL (pai fantasma). Backup em <db>.bak; verify no fim tem de dar OK."""
    _ok, _n, _tampered, dangling = await cmd_verify(db)
    if dangling:
        raise ValueError("refusing to rehash: dangling parents (omission) — fix the DAG first.")
    store = await _open(db)
    entries = [e async for e in store.stream()]
    if not entries:
        return 0, 0, 0
    shutil.copyfile(db, db + ".bak")                      # rollback barato
    tmp = db + ".rehash"
    if os.path.exists(tmp):
        os.remove(tmp)
    new_store = SQLiteEventStore(tmp)
    await new_store.initialize()
    idmap, changed = {}, 0
    for e in entries:                                     # seq = pais antes dos filhos
        ne = Entry(kind=e.kind, author=e.author, agent=e.agent, provider=e.provider,
                   model=e.model, summary=e.summary, body=e.body,
                   parents=[idmap.get(p, p) for p in e.parents],
                   ts=e.ts, dedup_key=e.dedup_key)        # ts/dedup preservados (fora do hash)
        idmap[e.id] = ne.id
        if ne.id != e.id:
            changed += 1
        await new_store.append(ne)
    for side in ("-wal", "-shm"):                         # sidecars velhos não podem "recuperar"
        for base in (db, tmp):                            # por cima do arquivo trocado
            if os.path.exists(base + side):
                os.remove(base + side)
    os.replace(tmp, db)
    n_view = await _write_view(await _open(db), out)
    ok2, n2, t2, d2 = await cmd_verify(db)
    if not ok2:
        raise ValueError(f"rehash produced a BROKEN ledger (bug) — restore from {db}.bak")
    return changed, n2, n_view


def cmd_schema() -> str:
    """O schema SQL da nuvem (Supabase), empacotado — cole no SQL Editor ou `lifeline schema | psql`."""
    from importlib.resources import files
    return files("lifeline").joinpath("schema.sql").read_text(encoding="utf-8")


# capture (zero-LLM): prefixo convencional do commit → kind do core. Qualquer outro → note.
_CAPTURE_KIND = {"feat": "feature", "feature": "feature", "fix": "fix", "bugfix": "fix",
                 "hotfix": "fix", "perf": "note", "refactor": "note", "docs": "note",
                 "chore": "note", "test": "note", "revert": "note"}
# trailers de commit não são o *porquê* — saem do body capturado
_TRAILER = re.compile(r"^(co-authored-by|signed-off-by|reviewed-by|cc|fixes|closes|refs?)[:#]",
                      re.IGNORECASE)


def _capture_kind(subject: str) -> str:
    m = re.match(r"^\s*(\w+)\s*(?:\(.*?\))?\s*[:!]", subject or "")
    return _CAPTURE_KIND.get(m.group(1).lower(), "note") if m else "note"


def _capture_why(body: str) -> str:
    """O *porquê* de um commit = o corpo escrito pelo humano, sem trailers. Curto demais
    (< 20 chars) = não há porquê escrito → abstém (Lei #5: capturar sem porquê é ledger rot)."""
    lines = [ln for ln in (body or "").splitlines() if not _TRAILER.match(ln.strip())]
    why = "\n".join(lines).strip()
    return why if len(why) >= 20 else ""


async def cmd_capture(db, author, last=20):
    """Captura LOCAL zero-LLM: rascunha PROPOSTAS a partir das MENSAGENS de commit (o texto
    humano — nunca o diff). kind pelo prefixo convencional; o corpo do commit é o porquê
    (obrigatório — sem corpo, abstém). Idempotente: o último sha visto fica em
    `<db>.capture.head`; re-rodar só olha commits novos. Tudo entra PENDENTE (HITL)."""
    if not sync.is_repo():
        raise ValueError("not a git repository here — capture reads git commit messages.")
    head_file = db + ".capture.head"
    since = None
    if os.path.exists(head_file):
        with open(head_file, encoding="utf-8") as f:
            since = f.read().strip() or None
    rng = [f"{since}..HEAD"] if since else ["-n", str(last)]
    r = sync._git(["log", "--no-merges", "--format=%H%x1f%s%x1f%b%x1e", *rng])
    if r.returncode != 0:
        raise ValueError(f"git log failed: {(r.stderr or '').strip()[:200]}")
    staging = _staging(db)
    await staging.initialize()
    proposed, skipped = [], 0
    records = [rec for rec in (r.stdout or "").split("\x1e") if rec.strip()]
    for rec in reversed(records):                       # ordem cronológica (git log é reverso)
        parts = rec.strip().split("\x1f")
        if len(parts) < 2:
            continue
        sha, subject = parts[0].strip(), parts[1].strip()
        why = _capture_why(parts[2] if len(parts) > 2 else "")
        if not why:
            skipped += 1                                # sem porquê escrito → não inventa
            continue
        pid = await staging.propose(
            kind=_capture_kind(subject), summary=subject[:200],
            body=f"{why}\n\n[captured from commit {sha[:12]}]",
            author=author, agent="lifeline-capture", provider="git", model="conventional-commits",
            parents=None)
        proposed.append((pid, _capture_kind(subject), subject[:200]))
    head = sync._git(["rev-parse", "HEAD"])
    if head.returncode == 0 and head.stdout.strip():    # marca o ponto visto (mesmo se 0 propostas)
        with open(head_file, "w", encoding="utf-8") as f:
            f.write(head.stdout.strip())
    return proposed, skipped


# ---- exam: Context Health (F2) — o quão pronto este ledger deixa uma IA nova -------------
# Score determinístico e transparente, 0–100. Não é vaidade: cada dimensão mede uma condição
# NECESSÁRIA para TTC→0 (uma IA conectar e responder o quê/por quê/decidido/próximo).
_EXAM_WHY_MIN = 40      # chars de porquê pra uma decisão contar como "com racional"
_EXAM_FRESH = ((7, 15), (30, 10), (90, 5))   # dias desde a última entrada → pontos


async def cmd_exam(db, budget=8000):
    """Examina a saúde de contexto da line. Integridade é PORTÃO (cadeia quebrada = reprovado):
    um score alto sobre um ledger adulterado seria a mentira perfeita. Retorna
    (score, grade, dims, suggestions, failed)."""
    from datetime import datetime, timezone
    ok, n_entries, tampered, dangling = await cmd_verify(db)
    if not ok:
        return 0, "F", [("integrity", 0, 20,
                         f"chain BROKEN: {len(tampered)} tampered, {len(dangling)} dangling")], \
               ["run `lifeline verify` and repair before anything else — a broken chain "
                "means the context can't be trusted at all"], True

    store = await _open(db)
    st = await StateEngine(store).reduce()
    now = datetime.now(timezone.utc)

    def _aware(ts):
        # view artesanal pode carregar ts NAIVE; aware-naive subtração é TypeError — trata como UTC
        return ts if ts.tzinfo is not None else ts.replace(tzinfo=timezone.utc)
    entries = [e async for e in store.stream()]
    dims, tips = [], []

    # 1) integridade (20) — já passou no portão
    dims.append(("integrity", 20, 20, f"chain verifies ({n_entries} anchored entries)"))

    # 2) identidade (10) — sem bootstrap, a IA não sabe nem O QUE é o projeto
    if st.get("project"):
        dims.append(("identity", 10, 10, "bootstrap present (the project knows what it is)"))
    else:
        dims.append(("identity", 0, 10, "no bootstrap entry"))
        tips.append("record the project's identity: lifeline log --kind bootstrap "
                    "--summary \"<what this is>\" --body \"<why it exists>\"")

    # 3) densidade de porquê (25) — decisões sem racional são o começo do ledger rot
    decisions = st.get("decisions", [])
    if decisions:
        with_why = sum(1 for d in decisions if len((d.get("body") or "").strip()) >= _EXAM_WHY_MIN)
        pts = round(25 * with_why / len(decisions))
        dims.append(("why-density", pts, 25,
                     f"{with_why}/{len(decisions)} decisions in force carry a written why"))
        if with_why < len(decisions):
            tips.append(f"{len(decisions) - with_why} decision(s) have no real why — supersede "
                        "each with a corrected entry that states the rationale")
    else:
        dims.append(("why-density", 0, 25, "no decisions in force"))
        tips.append("record the decisions that shape this project (kind=decision, body=the why)")

    # 4) direção (15) — sem thread aberta, a IA não sabe O QUE VEM a seguir
    opens = st.get("open_items", [])
    superseded = set(st.get("superseded", []))
    open_ts = [_aware(e.ts) for e in entries if e.kind == "open" and e.id not in superseded]
    pts = 10 if opens else 0
    if open_ts and (now - max(open_ts)).days <= 45:
        pts += 5
    label = (f"{len(opens)} open thread(s)" + ("" if not open_ts else
             f", newest {max(0, (now - max(open_ts)).days)}d old")) if opens else "no open threads"
    dims.append(("direction", pts, 15, label))
    if not opens:
        tips.append("record what's next: lifeline log --kind open --summary \"<the thread>\" "
                    "--body \"<why it matters>\"")

    # 5) frescor (15) — ledger que ninguém alimenta é diário que ninguém mantém
    if entries:
        age = (now - max(_aware(e.ts) for e in entries)).days
        pts = next((p for lim, p in _EXAM_FRESH if age <= lim), 0)
        dims.append(("freshness", pts, 15, f"last entry {age}d ago"))
        if pts < 15:
            tips.append("the ledger is going stale — wire capture (`lifeline capture` locally, "
                        "or the GitHub App on merged PRs) so the why records itself")
    else:
        dims.append(("freshness", 0, 15, "empty ledger"))

    # 6) sonda TTC (15) — o payload montado responde o quê/por quê/decidido/próximo?
    ctx = await ContextAssembler(StateEngine(store), budget_chars=budget).assemble()
    probes = [("what", bool(st.get("project"))),
              ("why/decided", "## Why / what's decided" in ctx and bool(decisions)),
              ("next", "## Open / next" in ctx),
              ("recent", "## Recent" in ctx)]
    hit = sum(1 for _, okp in probes if okp)
    dims.append(("ttc-probe", round(15 * hit / 4), 15,
                 "context answers: " + ", ".join(k for k, okp in probes if okp)))
    if hit < 4:
        tips.append("the assembled context is missing: "
                    + ", ".join(k for k, okp in probes if not okp))

    score = sum(p for _, p, _, _ in dims)
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 \
        else "D" if score >= 40 else "F"
    return score, grade, dims, tips, False


def _line_paths(name):
    """(db, view) de uma line pelo NOME — 'ledger'/None = a default. Reusa resolve_paths
    (única fonte do mapeamento nome→arquivos)."""
    return resolve_paths(None if name in (None, "ledger") else name, DEFAULT_DB, DEFAULT_OUT)


async def cmd_promote(src_line, dst_line, ids=None, kind=None):
    """Copia entrada(s) da line origem para a destino como ROOT (parents=[]), com nota de
    proveniência no body. Idempotente por content-addressing: mesmo conteúdo → mesmo id →
    re-promover deduplica (Lei #3). Corrections são recusadas (uma correção sem os pais dela
    não supersede nada no destino — seria ruído semântico)."""
    if src_line == dst_line:
        raise ValueError("promote: source and destination are the same line.")
    src_db, _ = _line_paths(src_line)
    dst_db, dst_out = _line_paths(dst_line)
    if not os.path.exists(src_db):
        raise ValueError(f"promote: source line '{src_line}' has no ledger ({src_db}).")
    src = await _open(src_db)
    if ids:
        targets = []
        for eid in await resolve_parents(src, ids):     # reusa expansão de prefixo (#G1)
            targets.append(await src.get(eid))
    else:
        st = await StateEngine(src).reduce()
        superseded = set(st.get("superseded", []))
        targets = [e async for e in src.stream()
                   if e.kind == kind and e.id not in superseded]
        if not targets:
            raise ValueError(f"promote: no live '{kind}' entries on line '{src_line}'.")
    dst = await _open(dst_db)
    promoted, dups = [], 0
    for e in targets:
        if e.kind == "correction":
            raise ValueError(f"promote: {e.id[:12]}… is a correction — corrections supersede "
                             "their parents and don't stand alone; promote the corrected truth instead.")
        prov = f"[promoted from {src_line}#{e.id[:8]}]"
        body = (e.body or "").strip()
        ne = Entry(kind=e.kind, author=e.author, agent=e.agent, provider=e.provider,
                   model=e.model, summary=e.summary,
                   body=f"{body}\n\n{prov}" if body else prov,
                   parents=[], ts=e.ts)                  # ROOT no destino; ts preserva o momento
        if await dst.append(ne):
            promoted.append(ne)
        else:
            dups += 1
    n = await _write_view(dst, dst_out) if promoted else 0
    return promoted, dups, n


async def cmd_init(db, out):
    """Inicializa a line (idempotente) e diz se já há contexto registrado. NÃO cria entradas:
    o bootstrap é HITL — a IA/humano PROPÕE e o humano aprova (anti-sujeira + nunca inferir)."""
    store = await _open(db)
    st = await StateEngine(store).reduce()
    bootstrapped = bool(st.get("project")) or bool(st.get("decisions"))
    await _write_view(store, out)                    # garante .lifeline/ + a view existindo
    return bootstrapped, st.get("entry_count", 0)


async def cmd_context(db, budget, query=None):
    store = await _open(db)
    recall = None
    if query:
        from lifeline.recall import SemanticRecall, make_embedder
        recall = SemanticRecall(store, make_embedder())   # LIFELINE_EMBEDDER=dense → semântico
    return await ContextAssembler(StateEngine(store), budget_chars=budget).assemble(query=query, recall=recall)


async def cmd_lines(root=LINES_DIR):
    if _STORE["kind"] == "supabase":                     # bug L4: a nuvem também tem lines
        from lifeline.cloud import SupabaseEventStore
        return await SupabaseEventStore(line=_STORE["line"]).lines()
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "*.db"))):
        name = os.path.splitext(os.path.basename(path))[0]
        store = SQLiteEventStore(path)
        await store.initialize()
        n = 0
        async for _ in store.stream():
            n += 1
        rows.append((name, n))
    return rows


async def cmd_push(db, out, message="lifeline: sync"):
    if not sync.is_repo():
        raise ValueError("not a git repository here. Run: git init && git remote add origin <url>")
    await cmd_rebuild(db, out)                  # garante a view textual atual
    sync.add_commit(".", message)               # ok se não houver nada a commitar
    r = sync.push(".")
    return r.returncode == 0, (r.stderr or r.stdout).strip()


async def cmd_pull(db, out):
    if not sync.is_repo():
        raise ValueError("not a git repository here.")
    r = sync.pull(".")
    if sync.has_conflict():
        return False, "merge CONFLICT in the view — resolve it in LIFELINE.md (it's readable) and run pull again."
    await cmd_migrate(out, db)                   # ingere o markdown mergeado (dedup por id)
    await cmd_rebuild(db, out)                   # normaliza a view a partir do .db unido
    ok, _n, _t, _d = await cmd_verify(db)        # merge que não verifica é sucesso mentiroso
    if not ok:
        return False, "merged, but the ledger is BROKEN after ingest — run `lifeline verify` for details."
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def _view_line_name(basename):
    """Nome da line a partir do arquivo de view: LIFELINE.md → 'ledger';
    LIFELINE.<name>.md → '<name>'; qualquer outro → None (não é view)."""
    if basename == "LIFELINE.md":
        return "ledger"
    if basename.startswith("LIFELINE.") and basename.endswith(".md"):
        name = basename[len("LIFELINE."):-len(".md")]
        return name or None
    return None


async def cmd_clone(url, dest):
    r = sync.clone(url, dest)
    if r.returncode != 0:
        return False, (r.stderr or r.stdout).strip()
    # Reconstrói o .db de CADA line clonada (bug L3: antes só a default era reconstruída —
    # LIFELINE.<name>.md ficava sem ledger). E VERIFICA cada uma: clone que não verifica é
    # sucesso mentiroso.
    rebuilt, broken = [], []
    for src in sorted(glob.glob(os.path.join(dest, "LIFELINE*.md"))):
        name = _view_line_name(os.path.basename(src))
        if not name:
            continue
        db = os.path.join(dest, LINES_DIR, f"{name}.db")
        await cmd_migrate(src, db)
        await cmd_rebuild(db, src)
        ok, _n, _t, _d = await cmd_verify(db)
        (rebuilt if ok else broken).append(name)
    if broken:
        return False, (f"cloned into {dest}, but verify FAILED for line(s): "
                       f"{', '.join(broken)} — run `lifeline verify` there.")
    names = ", ".join(rebuilt) if rebuilt else "none"
    return True, f"cloned into {dest} ({len(rebuilt)} line(s) rebuilt + verified: {names})"


def _parents_arg(s):
    return [x.strip() for x in s.split(",") if x.strip()] if s else None


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # UTF-8 em console legado (Windows cp1252)
    except Exception:
        pass

    p = argparse.ArgumentParser(prog="lifeline", description="Lifeline — a context runtime")
    p.add_argument("--db", default=DEFAULT_DB)
    p.add_argument("--line", default=None, help="line name (sugar: .lifeline/<line>.db + LIFELINE.<line>.md)")
    p.add_argument("--store", choices=["sqlite", "supabase"], default="sqlite",
                   help="ledger backend (M3 Tier 1: supabase reads SUPABASE_URL/KEY from the env)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def _entry_args(sp, with_out=False):
        sp.add_argument("--kind", required=True)
        sp.add_argument("--summary", required=True)
        sp.add_argument("--body", default="")
        sp.add_argument("--author", default=os.environ.get("LIFELINE_AUTHOR", "unknown"))
        sp.add_argument("--agent", default="human")
        sp.add_argument("--provider", default="none")
        sp.add_argument("--model", default="human")
        sp.add_argument("--parents", default=None, help="comma-separated ids")
        if with_out:
            sp.add_argument("--out", default=DEFAULT_OUT)

    pini = sub.add_parser("init", help="initialize the line and print the bootstrap protocol (HITL checkpoint)")
    pini.add_argument("--out", default=DEFAULT_OUT)
    _entry_args(sub.add_parser("log", help="human: append directly to the line (you're the approver)"), with_out=True)
    _entry_args(sub.add_parser("propose", help="propose an entry (HITL) — stays pending until approved"))

    sub.add_parser("review", help="list pending proposals (HITL curation)")
    pa = sub.add_parser("approve", help="seal pending proposal(s) into the line")
    pa.add_argument("pids", nargs="+", help="pids to approve, or 'all'")
    prj = sub.add_parser("reject", help="discard pending proposal(s)")
    prj.add_argument("pids", nargs="+", help="pids to reject, or 'all'")

    pr = sub.add_parser("rebuild", help="regenerate the view from the store")
    pr.add_argument("--out", default=DEFAULT_OUT)
    sub.add_parser("verify", help="check the ledger's integrity")
    pm = sub.add_parser("migrate", help="ingest an existing markdown into the store")
    pm.add_argument("--from", dest="src", required=True)
    pm.add_argument("--strict", action="store_true",
                    help="fail if a recorded id doesn't match the recomputed content (tamper check)")
    pc = sub.add_parser("context", help="print the assembled context")
    pc.add_argument("--budget", type=int, default=8000)
    pc.add_argument("--query", default=None, help="prioritize what's relevant to the task (Layer 3)")
    prh = sub.add_parser("rehash", help="recompute every id under the current canonical scheme "
                                        "(one-shot migration after a hash-scheme upgrade)")
    prh.add_argument("--out", default=DEFAULT_OUT)
    ppro = sub.add_parser("promote", help="copy entries from one line into another as roots "
                                          "(idempotent — re-promoting dedups by content)")
    ppro.add_argument("--from", dest="src_line", required=True, help="source line name")
    ppro.add_argument("--to", dest="dst_line", required=True, help="destination line name")
    ppro.add_argument("--id", dest="ids", default=None, help="comma-separated ids (prefixes ok)")
    ppro.add_argument("--kind", dest="pkind", default=None,
                      help="promote every non-superseded entry of this kind instead of --id")
    pex = sub.add_parser("exam", help="Context Health: score 0-100 of how ready this line leaves "
                                      "a fresh AI (what/why/decided/next) + concrete gaps")
    pex.add_argument("--json", action="store_true", dest="as_json",
                     help="machine-readable output (score, dims, suggestions)")
    pex.add_argument("--budget", type=int, default=8000)
    pcap = sub.add_parser("capture", help="draft proposals from recent git commit messages "
                                          "(zero-LLM; the commit body is the why — no body, no draft)")
    pcap.add_argument("--last", type=int, default=20, help="commits to scan on the FIRST run "
                                                           "(after that, only commits newer than the last capture)")
    pcap.add_argument("--author", default=os.environ.get("LIFELINE_AUTHOR", "unknown"))
    sub.add_parser("lines", help="list the project's lines (.lifeline/*.db)")
    sub.add_parser("schema", help="print the cloud SQL schema (Supabase) — paste it into the SQL Editor")

    ppush = sub.add_parser("push", help="git sync: rebuild + commit + push the view")
    ppush.add_argument("--out", default=DEFAULT_OUT)
    ppull = sub.add_parser("pull", help="git sync: pull + rebuild the .db from the merged view")
    ppull.add_argument("--out", default=DEFAULT_OUT)
    pclone = sub.add_parser("clone", help="git clone <url> <dir> and rebuild the .db")
    pclone.add_argument("url")
    pclone.add_argument("dest")

    args = p.parse_args(argv)
    db, out = resolve_paths(args.line, args.db, getattr(args, "out", DEFAULT_OUT))

    _STORE["kind"] = args.store                  # reset explícito a cada chamada (sem vazar entre runs)
    _STORE["line"] = args.line or "ledger"
    if args.store == "supabase" and args.cmd in _LOCAL_ONLY:
        print(f"'{args.cmd}' is specific to the local store (git/HITL/SQLite). "
              f"With --store supabase use: log, context, verify, rebuild, migrate.")
        return 1

    try:
        return _dispatch(args, db, out)
    except ValueError as ex:                          # validation/usage → direct message
        print(f"error: {ex}")
        return 1
    except Exception as ex:                            # network/HTTP/unexpected → no raw traceback
        print(f"unexpected error ({type(ex).__name__}): {ex}")
        return 1


def _dispatch(args, db, out) -> int:
    if args.cmd == "init":
        bootstrapped, n = asyncio.run(cmd_init(db, out))
        if bootstrapped:
            print(f"This line already has context ({n} entries) — nothing to do. See: lifeline context")
        else:
            print(BOOTSTRAP_HEADER.replace("## ", "").strip())
            for line in BOOTSTRAP_PROTOCOL:
                print(line)
            print("\nPropose: lifeline propose --kind bootstrap --summary \"…\" --body \"the why\"")
            print("Approve: lifeline review   →   lifeline approve all")
        return 0

    if args.cmd == "log":
        e, inserted, n = asyncio.run(cmd_log(
            db, out, args.kind, args.summary, args.body, args.author, args.agent,
            args.provider, args.model, _parents_arg(args.parents)))
        print(f"#{n:04d} {'recorded' if inserted else 'duplicate (idempotent)'}: {e.kind} — {e.id[:12]}…")
        print(f"{out} regenerated ({n} entries).")
        return 0

    if args.cmd == "propose":
        try:
            pid = asyncio.run(cmd_propose(db, args.kind, args.summary, args.body, args.author,
                                          args.agent, args.provider, args.model, _parents_arg(args.parents)))
        except ValueError as ex:
            print(f"rejected: {ex}")
            return 1
        print(f"proposal #{pid} queued (PENDING). Curate: lifeline review")
        return 0

    if args.cmd == "review":
        rows = asyncio.run(cmd_review(db))
        if not rows:
            print("No pending proposals.")
            return 0
        print(f"{len(rows)} pending proposal(s) (HITL):\n")
        for r in rows:
            print(f"  #{r['pid']} [{r['kind']}] {r['summary']}  — by {r['provider']}/{r['model']}")
            if r["body"]:
                s = r["body"].strip().replace("\n", " ")
                print(f"        {s[:160] + ('…' if len(s) > 160 else '')}")
        print("\nApprove: lifeline approve <pid|all>    ·    Reject: lifeline reject <pid|all>")
        return 0

    if args.cmd == "approve":
        approved, n, duplicates, errors = asyncio.run(cmd_approve(db, out, args.pids))
        if approved:
            print(f"{approved} proposal(s) approved and sealed into the line. {out} regenerated ({n} entries).")
        elif not duplicates and not errors:
            print("Nothing approved (invalid pids or no pending proposals).")
        if duplicates:
            print(f"{duplicates} proposal(s) already in the line (dedup) — marked 'duplicate', not re-entered.")
        for pid, reason in errors:
            print(f"proposal #{pid} NOT approved (still pending): {reason}")
        return 0

    if args.cmd == "reject":
        print(f"{asyncio.run(cmd_reject(db, args.pids))} proposal(s) rejected.")
        return 0

    if args.cmd == "rebuild":
        print(f"{out} regenerated ({asyncio.run(cmd_rebuild(db, out))} entries).")
        return 0

    if args.cmd == "verify":
        ok, n, tampered, dangling = asyncio.run(cmd_verify(db))
        if ok:
            print(f"OK: {n} entries intact (content anchored + DAG closed).")
        else:
            print(f"BROKEN: {n} entries, WITH FAILURES.")
            for i in tampered:
                print(f"  tampered (id ≠ content): {i[:12]}…")
            for child, parent in dangling:
                print(f"  ghost parent: {child[:12]}… points to {parent[:12]}… (missing — omission?)")
        return 0 if ok else 1

    if args.cmd == "migrate":
        n = asyncio.run(cmd_migrate(args.src, db, strict=args.strict))
        print(f"Migrated {n} entries from {args.src} to {db}.")
        return 0

    if args.cmd == "exam":
        score, grade, dims, tips, failed = asyncio.run(cmd_exam(db, budget=args.budget))
        if args.as_json:
            print(json.dumps({"score": score, "grade": grade, "failed": failed,
                              "dimensions": [{"name": n, "points": p, "max": m, "detail": d}
                                             for n, p, m, d in dims],
                              "suggestions": tips}, indent=2))
            return 1 if failed else 0
        print(f"Context Health: {score}/100  ({grade})")
        for name, pts, mx, detail in dims:
            mark = "x" if pts == 0 else ("~" if pts < mx else "+")
            print(f"  [{mark}] {name:<12} {pts:>3}/{mx:<3} {detail}")
        if tips:
            print("\nSuggestions:")
            for t in tips:
                print(f"  - {t}")
        print(f"\nShareable: Lifeline Context Health {score}/100 ({grade})")
        return 1 if failed else 0

    if args.cmd == "capture":
        proposed, skipped = asyncio.run(cmd_capture(db, args.author, last=args.last))
        for pid, kind, summary in proposed:
            print(f"proposal #{pid} [{kind}] {summary[:70]}")
        if proposed:
            print(f"\n{len(proposed)} proposal(s) drafted from commit messages — PENDING "
                  f"(curate: lifeline review).")
        if skipped:
            print(f"{skipped} commit(s) skipped — no written why in the commit body (honest abstention).")
        if not proposed and not skipped:
            print("Nothing new to capture.")
        return 0

    if args.cmd == "rehash":
        changed, total, _nv = asyncio.run(cmd_rehash(db, out))
        if total == 0:
            print("Nothing to rehash (empty ledger).")
        else:
            print(f"Rehashed {total} entries ({changed} id(s) changed) — verify OK. "
                  f"Backup: {db}.bak · {out} regenerated.")
        return 0

    if args.cmd == "promote":
        if bool(args.ids) == bool(args.pkind):
            print("error: use exactly one of --id or --kind")
            return 1
        promoted, dups, n = asyncio.run(cmd_promote(
            args.src_line, args.dst_line, _parents_arg(args.ids), args.pkind))
        for e in promoted:
            print(f"promoted [{e.kind}] {e.summary[:60]} -> {args.dst_line} ({e.id[:12]}…)")
        if dups:
            print(f"{dups} already promoted (dedup by content) — no-op.")
        if promoted:
            print(f"LIFELINE.{args.dst_line}.md regenerated ({n} entries)."
                  if args.dst_line != "ledger" else f"LIFELINE.md regenerated ({n} entries).")
        return 0

    if args.cmd == "schema":
        print(cmd_schema())
        return 0

    if args.cmd == "context":
        print(asyncio.run(cmd_context(db, args.budget, args.query)))
        return 0

    if args.cmd == "lines":
        rows = asyncio.run(cmd_lines())
        if not rows:
            print("No lines yet. Create one with: lifeline log [--line <name>] --kind … --summary …")
            return 0
        for name, n in rows:
            label = f"{name} (default)" if name == "ledger" else name
            _, view = _line_paths(name)                 # fonte única do mapeamento nome→view
            print(f"  {label:<22} {n:>4} entries   → {view}")
        return 0

    if args.cmd == "push":
        try:
            ok, msg = asyncio.run(cmd_push(db, out))
        except ValueError as ex:
            print(f"error: {ex}")
            return 1
        print(("push OK — line synced. " if ok else "push failed: ") + msg)
        return 0 if ok else 1

    if args.cmd == "pull":
        try:
            ok, msg = asyncio.run(cmd_pull(db, out))
        except ValueError as ex:
            print(f"error: {ex}")
            return 1
        print(("pull OK — .db rebuilt from the merged view. " if ok else "") + msg)
        return 0 if ok else 1

    if args.cmd == "clone":
        ok, msg = asyncio.run(cmd_clone(args.url, args.dest))
        print(msg)
        return 0 if ok else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
