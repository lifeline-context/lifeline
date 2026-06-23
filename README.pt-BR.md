# Lifeline

> **Runtime de contexto para desenvolvimento com IA.** O projeto guarda *por que* ele
> é o que é — e qualquer IA conecta e **já sabe**, sem humano reexplicando.

🌐 **Português** · [English](README.md)

[![pypi](https://img.shields.io/pypi/v/lifeline-context)](https://pypi.org/project/lifeline-context/) ![status](https://img.shields.io/badge/status-beta-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![tests](https://img.shields.io/badge/tests-153%20passing-brightgreen) ![license](https://img.shields.io/badge/license-FSL--1.1--MIT-blue)

É, em uma frase, **o "git do raciocínio"**: assim como o git versiona *o quê* mudou no
código, o Lifeline versiona *por quê* — decisões, reversões, incidentes, o estado atual —
num ledger append-only, content-addressed, que vive dentro do projeto. Qualquer modelo
(Claude, GPT, Gemini), em qualquer sessão, reconstrói o contexto ao conectar via MCP.

---

## O problema

Assistentes de IA são **stateless entre sessões**. A cada nova sessão, agente ou provider,
o humano vira o barramento de memória — reexplicando decisões que já existiam. A correção
ingênua (um log markdown vivo) funciona até estourar a janela de contexto. Ferramentas de
"memória" guardam texto/vetores sem proveniência → recall alucinado.

## A ideia

O **norte** é uma métrica única — **Tempo-até-Contexto (TTC) → 0** — operacionalizada por um
teste de aceitação:

> Uma IA nova conecta, **sem humano no meio**, e responde corretamente:
> **o quê / por quê / o que está decidido / o que vem a seguir?**

O Lifeline guarda a "linha de vida" do projeto (a `LIFELINE.md`) e a torna
**consultável, comprimível e ancorada**, para nunca estourar a janela e nunca alucinar.

---

## Instalação

```bash
pip install lifeline-context        # quando publicado no PyPI
pip install -e .                    # ou, da raiz do repo (dev) → instala lifeline, lifeline-mcp, lifeline-mcp-remote
pip install -e ".[cloud]"           # opcional: modo nuvem (Supabase) — puxa httpx explicitamente
```

Dependências: `pydantic`, `aiosqlite`, `mcp`, `httpx`. Python ≥ 3.10.

## Quickstart (CLI)

```bash
# Em QUALQUER projeto seu — cada projeto ganha seu próprio .lifeline/ledger.db:
lifeline log --kind bootstrap --summary "Funda o projeto X" --body "API de cobrança multi-tenant."
lifeline log --kind decision  --summary "Banco: PostgreSQL"  --body "ACID exigido por auditoria."

lifeline context                       # imprime a verdade atual montada (o que uma IA lê)
lifeline context --query "banco"       # prioriza o que é relevante à tarefa (Camada 3)
lifeline verify                        # confere a integridade da cadeia
```

A `LIFELINE.md` se regenera a cada `log` — **não edite à mão**. Num clone novo sem
`.lifeline/`, reconstrua o cache com `lifeline migrate --from LIFELINE.md`.

**Adotando no meio do projeto (brownfield)?** O Lifeline registra o *porquê* **para frente** — não
o reconstrói a partir do código ou do histórico do git. Então instalar num projeto em andamento começa
**vazio**. Rode `lifeline init` (ou só conecte sua IA — o contexto vazio imprime o mesmo call-to-action):
ele conduz um **checkpoint de bootstrap** único — a IA lê seus docs de raciocínio (README, ADRs,
descrições de PR), faz algumas perguntas do *porquê*, e **propõe** entradas granulares (HITL) que você
aprova. Depois disso, o loop corre para frente. O *porquê* nunca é inferido do código (Leis #1/#5).

## O loop (faça os dois lados)

- **Ao conectar:** carregue o contexto (`lifeline context` ou o resource MCP) antes de agir.
- **Ao trabalhar:** a cada decisão/feature/fix/incidente, **anexe** (`lifeline log` ou
  `lifeline_append`). Reverteu algo? `lifeline_recontextualize` (supersede por id).

## Conceitos centrais

- **Entry** — a unidade atômica. Content-addressed: `id = sha256(kind, author, agent,
  provider, model, summary, body, pais-ordenados)`. `ts` e `dedup_key` ficam **fora** do
  hash → o mesmo conteúdo gera o mesmo `id` em qualquer máquina (base do dedup e do sync).
- **As 3 camadas de memória** (todas ancoradas no ledger imutável): **Ledger** (DAG hasheado,
  fonte de verdade) · **Estado** (verdade atual reduzida via reducers) · **Recall** (relevância
  ancorada ao evento de origem).
- **Supersessão** — uma `correction` que referencia o `id` de outra entrada a remove da
  verdade atual. Append-only: o passado nunca é editado.
- **Âncora anti-alucinação** — todo item que a IA lê carrega o hash do evento de origem.

Detalhe completo em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Para IAs / AI agents

**Qualquer IA entende este projeto sem ninguém explicar.** Leia a line ([`LIFELINE.md`](LIFELINE.md),
comece pela #0001), ou rode `lifeline context`, ou via MCP o resource `lifeline://project/context`.
Onboarding tool-agnóstico em [`AGENTS.md`](AGENTS.md) (e [`CLAUDE.md`](CLAUDE.md) p/ Claude Code).

## As 7 leis (a constituição)

1. **Nenhuma memória sem âncora imutável** (anti-alucinação). 2. **Append-only.**
3. **Content-addressing determinístico.** 4. **Storage agnóstico de provider; entrega no formato dele.**
5. **O *porquê* pesa mais que o *quê*.** 6. **Budget é first-class** (truncamento explícito). 7. **MCP-native.**

## Non-goals

NÃO é OS cognitivo, MMU, orquestrador de agentes, workflow engine, substituto do git, nem
executor/treinador. **Registra raciocínio, não execução.**

## Do local pra nuvem

Tudo é content-addressed → **subir uma line local pra nuvem é lossless e idempotente**:
```bash
lifeline --store supabase migrate --from LIFELINE.md   # seed (repetível, não duplica)
lifeline --store supabase context
```
Setup da nuvem: [`docs/M3_TIER1_SUPABASE.md`](docs/M3_TIER1_SUPABASE.md). Conectar nos clientes: [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

## Status

**Beta.** Núcleo **local single-user** sólido — correção travada por testes (determinismo,
anti-adulteração, detecção de omissão, supersessão reversível, round-trip ponto-fixo, abstenção
do recall, idempotência sob appends concorrentes). **Nuvem (M3) funcional e validada ao vivo.**
153 testes verdes (147 offline + 6 live-gated); CI no GitHub Actions. Conectores web hospedados
funcionam via o **OAuth Server nativo do Supabase** (o MCP remoto é um Resource Server que valida o
JWT por JWKS); validação end-to-end ao vivo **concluída** (401 sem token, 200 com JWT; #0049, #0079, #0090).

**Limites honestos hoje:** recall default é lexical (palavras); o **semântico denso** é opt-in
(`pip install lifeline-context[embeddings]` + `LIFELINE_EMBEDDER=dense`, #0029). Nuvem **paga**
turnkey ainda precisa de billing — hoje é **core source-available + traga-seu-Supabase**. Sem
retry/backoff no adapter de nuvem ainda (só log+raise).

## Licença

[FSL-1.1-MIT](LICENSE) (Functional Source License) — **source-available**: leia, rode, modifique e
auto-hospede para qualquer fim *exceto* oferecer como serviço comercial concorrente; **converte para
MIT em 2 anos** após cada release. (Versões ≤ 0.2.0 foram publicadas sob MIT e seguem MIT.) O que se
paga é o **hub** hospedado, não o código.
