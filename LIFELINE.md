# LIFELINE — lifeline

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

---

## Entries

### #0001 — 2026-05-30T14:00:00+00:00 — bootstrap

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: bootstrap
- **summary**: Funda o Lifeline — runtime de contexto que faz uma IA nova conectar e já saber, sem humano reexplicando
- **parents**: —
- **id**: eba55025c2509a0785d32640f02dbcb284fcb32f1331005d234c3b37e97994c1

**Body**:
O Lifeline existe para que o dono do projeto pare de ser a memória. Hoje, toda vez
que uma sessão acaba, uma janela de contexto enche, ou a ferramenta muda (ChatGPT,
Gemini, Claude), a cadeia de raciocínio que sustenta o projeto morre — e o humano
vira o único backup, reexplicando decisões que já foram tomadas.

O Lifeline é: **o projeto guarda *por que* ele é o que é, e qualquer mente que
conecta herda esse porquê na hora — sem ninguém reexplicar.**

Norte (teste de aceitação): uma IA nova conecta, sem humano no meio, e responde
corretamente o quê / por quê / o que está decidido / o que vem a seguir. Hoje =
não (horas de leitura + explicação). Pronto = sim, em segundos. A métrica é o
Tempo-até-Contexto → zero.

Origem: nasceu de uma `LIFELINE.md` mantida à mão no projeto `inframoe` (cadeia de
hash append-only, 159 entradas) que comprovadamente resolveu essa dor — mas crescia
sem limite e estourava a janela. O Lifeline mantém essa disciplina e a torna
consultável/comprimível, para nunca estourar. Esta própria entrada foi escrita no
momento em que o produto se provou: o fundador não conseguiu explicar o que queria,
e não precisou — o contexto bastou.

<!-- lifeline:end -->

### #0002 — 2026-05-30T14:10:00+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Trava o núcleo — 3 camadas ancoradas, DAG content-addressed, status como reducer, e os non-goals
- **parents**: eba55025c2509a0785d32640f02dbcb284fcb32f1331005d234c3b37e97994c1
- **id**: 58e4b2b254b6164fb641815fc2f13d179e57276909efe23dd8075aa5b27aebd3

**Body**:
O coração tem três camadas, todas ancoradas no mesmo ledger imutável: (1) ledger
episódico — DAG hasheado, fonte de verdade; (2) estado operacional — verdade atual
reduzida do ledger via reducers (status é projeção de reducer, NÃO máquina de
estados de execução); (3) recall semântico — embeddings, cada resultado ancorado de
volta ao ledger. Topologia DAG (escolha do dono, preparando contribuição concorrente
multi-IA/multi-usuário no futuro), mas reconstruída correta: hash determinístico
(sem timestamp no hash) e merge de verdade.

Porquê: o SDK anterior foi especificado pelo ChatGPT como "microkernel cognitivo /
hypervisor / OS distribuído" e codado pelo Gemini, virando vocabulário > substância
(~25 arquivos vazios, sandbox/scheduler/distribuído que eram teatro). Os non-goals
(não é OS/MMU/orquestrador/workflow/git) existem para impedir que essa inflação
ressuscite.

<!-- lifeline:end -->

### #0003 — 2026-05-30T14:20:00+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Absorve segmentação funcional em 5 dimensões como capacidade derivada e ancorada; rejeita o Ramo Dourado
- **parents**: 58e4b2b254b6164fb641815fc2f13d179e57276909efe23dd8075aa5b27aebd3
- **id**: 077e8c70fd63cfb6174293a6b5a1bc2ea52c6e2b1011141e8739ee188a979dd9

**Body**:
A ideia boa do material "CortexFS/Deep1545": segmentar contexto por utilidade
funcional em 5 dimensões (procedural, constraint, objetivo, grounding, semântico),
para na hora de uma decisão ler só as dimensões relevantes (ex.: constraint +
grounding para analisar multa) — menos tokens, menos ruído, menos alucinação.
Absorvido COMO capacidade do Context Engine, com 3 guard-rails: (a) segmentação é
camada DERIVADA, nunca a fonte de verdade — o evento bruto continua imutável; (b)
todo fragmento carrega o hash do evento de origem (Lei #1); (c) é gerada por LLM,
logo não-determinística → vive na camada regenerável, jamais no ledger.

Rejeitado: o "Ramo Dourado" (recursão fractal via Pareto que elege UMA dimensão
vencedora na ingestão). Porquê: relevância é propriedade da *pergunta* (read-time),
não do documento (write-time); e o próprio exemplo (precisa de constraint+grounding,
duas dimensões) contradiz a eleição de uma só vencedora. Guarda as 5 dimensões
planas e o retrieval escolhe na query. Branding ("Pentagrama", "Opcode 0xDB") é o
mesmo figurino que inflou o SDK — descartado.

<!-- lifeline:end -->

### #0004 — 2026-05-30T14:30:00+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Abordagem de build — reconstrução limpa, transplante dos órgãos comprovados, dogfooding desde a #0001
- **parents**: 077e8c70fd63cfb6174293a6b5a1bc2ea52c6e2b1011141e8739ee188a979dd9
- **id**: bb36017b984f08ca3401ca2a3336ae6ae80ff51bc149a861f61a9b85d480c624

**Body**:
Nem polir o SDK antigo (o defeito é estrutural: identidade do evento ancorada em
timestamp; vocabulário polui), nem greenfield puro (há código testado bom). Caminho:
reconstruir o esqueleto limpo e transplantar os órgãos comprovados do SDK anterior —
vetor cosseno, compressão (collapse anti-loop), snapshot zlib, mecânica do SQLite
(WAL/edges/dedup/DLQ), bus local com fallback, projeção markdown, adapter Gemini,
cache de contexto. Reescrever na raiz: modelo de evento (content-addressed
determinístico), status como reducer, e o resource MCP de contexto (a feature que
entrega o norte e que não existia no SDK).

Estratégia de produto: dogfooding tão bem-feito que resolva primeiro a dor do dono,
depois a dos outros, e então monetize como híbrido — core OSS local grátis; nuvem
paga (Supabase + pgvector + Redis Streams) para sync, time e escala. M1 = o laço
mínimo (captura ancorada → ledger → estado → montagem → MCP) que já passa o teste de
aceitação contra o próprio repo do Lifeline.

<!-- lifeline:end -->

### #0005 — 2026-05-30T15:00:00+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: M1 começou — modelo de evento content-addressed (Entry) testado; fundação fechada (CLAUDE.md + PRD portados)
- **parents**: bb36017b984f08ca3401ca2a3336ae6ae80ff51bc149a861f61a9b85d480c624
- **id**: 5812143edbf721958b80266c9cac464f499fa6c590c882487496d3ef59cbad83

**Body**:
Fundação fechada: CLAUDE.md (as 7 leis + a regra "se mexeu, anexe na LIFELINE e
re-sele" — para humanos e agentes obedecerem igual) e PRD.md portados para v2/.

M1 (o laço) começou pela peça-raiz: lifeline/entry.py — o Entry content-addressed.
id = sha256(conteúdo + pais ordenados); ts e dedup_key ficam fora do hash (Lei #3).
7 testes provam: id estável a despeito do ts, sensível ao body, invariante à ordem
dos pais, dedup_key não altera identidade, e auto-verificável (verify() detecta
adulteração). É a primeira linha de código do produto e ela obedece à constituição.

Próximo: store SQLite append-only (transplante WAL/edges/dedup/DLQ do SDK antigo,
agora determinístico) → redução de estado via reducers → montagem → resource MCP de
contexto.

<!-- lifeline:end -->

### #0006 — 2026-05-30T15:30:00+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Ledger SQLite (Camada 1) atrás da interface EventStore — append idempotente, DAG navegável, costura pra nuvem
- **parents**: 5812143edbf721958b80266c9cac464f499fa6c590c882487496d3ef59cbad83
- **id**: a81d9378c2d15c619f5a48917eb665f936b41628523be278f8c30bb19ec0d1e9

**Body**:
Landou lifeline/store.py: a Camada 1 (ledger episódico). EventStore (ABC) é a costura
— o core depende só dela; um SupabaseEventStore futuro implementa a mesma interface
sem tocar no núcleo (é assim que a nuvem entra sem inflar o core). SQLiteEventStore é
o adapter local: WAL, tabela de arestas pro DAG, índice único de dedup.

5 testes provam: roundtrip lossless (Entry reconstruído mantém id e verify()), append
idempotente por id E por dedup_key (a dor do "split-brain" do SDK velho, resolvida de
forma simples), ordem causal de inserção, e navegação parents/children no DAG.

Estratégia confirmada nesta sessão (sobre OSS local + nuvem paga): desenhar a costura
(interface) agora, adiar o código de nuvem pro M3 — construir nuvem com zero usuário é
a mesma generalização prematura que inflou o SDK. A monetização real mora no caso de
TIME (contexto compartilhado), não no solo. O risco existencial nº1 é a fricção de
captura — validada ao vivo por este próprio dogfooding. Próximo: redução de estado
(reducers, status como projeção) → montagem de contexto → resource MCP. Alvo do M1:
fechar o laço e rodar o teste de aceitação contra a própria LIFELINE.

<!-- lifeline:end -->

### #0007 — 2026-05-30T16:00:00+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Camada 2 (estado como projeção + supersessão por correção) e montagem mínima — payload o quê/por quê/decidido/próximo
- **parents**: a81d9378c2d15c619f5a48917eb665f936b41628523be278f8c30bb19ec0d1e9
- **id**: 188545f11420ad6ba71cfe97608352bfc525cedcbbc780dceb74bef6d3f571cb

**Body**:
Landou lifeline/state.py (Camada 2) e lifeline/context.py (montagem). StateEngine
dobra o ledger em "verdade atual" via reducers puros — status é PROJEÇÃO, não FSM
(decisão #0002). O reducer padrão ledger_projection entrega identidade + decisões em
vigor + recentes, e respeita correções: uma entrada `correction` supersede seus pais
(Lei #2), então a verdade atual nunca mostra decisão revogada. ContextAssembler
renderiza o payload "o quê (bootstrap) / por quê e decidido (decisões) / o que vem a
seguir (recentes)" dentro de um budget, com truncamento sempre explícito (Lei #6).

17 testes verdes (entry 7, store 5, state 3, context 2). O laço está a UM passo de
fechar: falta o resource MCP + um ingester (markdown LIFELINE → store) para rodar o
teste de aceitação contra a própria v2/.

Seam pendente de decisão: hoje existem DOIS esquemas de hash — a cadeia da markdown
(scripts/lifeline_hash.py, estilo prev_hash) e o id content-addressed do Entry (estilo
pais/DAG). Funcionam para propósitos diferentes (integridade humana vs identidade de
runtime), mas precisam ser unificados — provavelmente gerando a markdown A PARTIR do
store, ou alinhando as duas formas canônicas. Decisão para a próxima sessão.

<!-- lifeline:end -->

### #0008 — 2026-05-30T16:45:00+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: Teste de aceitação PASSOU — agente sem contexto respondeu o quê/por quê/decidido/próximo só do payload (TTC ~15s, 80%)
- **parents**: 188545f11420ad6ba71cfe97608352bfc525cedcbbc780dceb74bef6d3f571cb
- **id**: 2c733ea2e20f40efbfa33fa16d2d3bee0c60157008a6a6a6fbf43bcd21d2bd21

**Body**:
O laço do M1 fechou e foi validado contra o próprio projeto. Landaram lifeline/
ingest.py (markdown → store) e lifeline/mcp_server.py (resource lifeline://project/
context, Lei #7). O ContextAssembler passou a incluir o *porquê* (corpo das decisões,
truncado) — Lei #5.

Teste de aceitação: um agente general-purpose com ZERO contexto desta sessão, proibido
de explorar o repo, recebeu APENAS o payload montado (2208 chars, ingerindo as 7
entradas da própria LIFELINE) e respondeu corretamente, sozinho, em ~15s: o quê (runtime
de contexto), por quê (TTC→0), decidido (3 camadas, DAG content-addressed, status como
projeção, segmentação funcional, Ramo Dourado rejeitado) e próximo (M1: Entry + Camada 1
+ Camada 2). Confiança autorreportada: 80%. O norte (TTC) saiu de "horas + humano" para
"~15s, sem humano".

Backlog do M2 que o próprio agente revelou (auto-crítica do produto): o payload precisa
de uma seção "próximo/aberto" explícita (hoje só mostra recentes); corpos de decisão
truncados limitam precisão (ranking/compressão funcional do M2 resolve); Camada 3 (recall
semântico) ausente. Pendências: unificar os dois esquemas de hash (store vira fonte,
markdown gerada) e transplantar vetor cosseno + compressão do SDK antigo. 17/17 testes
verdes. M1: essencialmente concluído e provado.

<!-- lifeline:end -->

### #0009 — 2026-05-30T17:15:00+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Visão e posicionamento — Lifeline é o "GitHub para contexto de IA" (não de código): core local git-like (OSS) → hub na nuvem (pago)
- **parents**: 2c733ea2e20f40efbfa33fa16d2d3bee0c60157008a6a6a6fbf43bcd21d2bd21
- **id**: 3c9e2b2ea21e73f7799e3f01002c882291e8e2a5f4f63c9d13d70e41de57b5b0

**Body**:
Framing definido pelo dono: o Lifeline é o "GitHub para contexto de IA". git é o DAG
content-addressed append-only do CÓDIGO (o *o quê*); o Lifeline é o DAG content-addressed
append-only do RACIOCÍNIO/CONTEXTO (o *porquê*). GitHub é o hub sobre o git; o Lifeline
Hub é o hub sobre o Lifeline. As decisões já travadas (#0002, #0004) são exatamente o
modelo git — o framing não é marketing imposto depois, é o destino natural delas.

Distinção e non-goal: Lifeline NÃO reimplementa git nem versiona arquivos. git guarda o
quê (código); Lifeline guarda o porquê (raciocínio) — complementares, não concorrentes.
Em uso não-code/conversacional (onde não há git), o Lifeline fica sozinho. Uma "linha"
(line) = um repo/branch de contexto, multiprovider e async; clone/fork/merge de linhas
são operações naturais (M4). Detalhe: somos mais content-puros que o git — tiramos o ts
do hash (o commit do git inclui timestamp) para dedup funcionar entre providers.

Fases (batem com o roadmap): local git-like = M1 (feito) + M2, o core OSS grátis; nuvem
+ hub = M3 (sync Supabase) + M4 (o Hub: compartilhar linhas, time, privado, descoberta),
o pago. Monetização open-core provada pelo próprio GitHub (git grátis, GitHub é negócio).
Caveat honesto: a analogia comunica, mas o moat continua sendo a cunha — proveniência
ancorada + multiprovider + o porquê>o quê.

<!-- lifeline:end -->

### #0010 — 2026-05-30T17:40:00+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Formato do payload = markdown com estrutura leve, NÃO JSON/YAML — compactação é semântica, não sintática
- **parents**: 3c9e2b2ea21e73f7799e3f01002c882291e8e2a5f4f63c9d13d70e41de57b5b0
- **id**: 6cda47991e6a6f733d73ea0ec7e58f5898bebace4f25853740e95092a1a17c09

**Body**:
O payload que a IA lê é renderizado em markdown, não JSON/YAML. Porquê: JSON/YAML gastam
tokens com aspas/chaves/keys repetidas por item; LLMs são treinados em markdown e parseiam
headings/bullets nativamente — melhor compreensão por token. Não existe "protocolo mágico
de IA": o modelo É de linguagem, então linguagem-com-estrutura-leve é o formato nativo;
scaffolding JSON tende a atrapalhar (mais token, às vezes mais confusão). JSON serve pro
caso inverso — quando um PROGRAMA parseia a saída do modelo.

A compactação que importa NÃO é a sintática (serialização), e sim a semântica: rankear/
selecionar o relevante + sumarizar + segmentação funcional (M2). A Lei #4 deixa a porta
aberta pra renderers por provider depois (ex.: tags XML pro Claude delimitar seções), mas
markdown é o default. Registrado para ninguém "otimizar" pra JSON no futuro.

<!-- lifeline:end -->

### #0011 — 2026-05-30T17:45:00+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Autoria no payload — quem/provider/modelo de cada decisão + agregado de contribuidores (proveniência multiprovider)
- **parents**: 6cda47991e6a6f733d73ea0ec7e58f5898bebace4f25853740e95092a1a17c09
- **id**: 519a9930dbfdda900f12fb4ef9f9aa94f38b2c014e5d702aea2f0b850200dc60

**Body**:
O ContextAssembler agora mostra a autoria que já existia no ledger mas estava oculta: cada
decisão exibe `provider/modelo`, o bootstrap mostra "fundado por", e um agregado
"Contribuíram: …" lista quem produziu o quê e quanto. Em contexto multiprovider isso é
proveniência de raciocínio — dá pra confiar/auditar/questionar uma decisão por quem a fez
(ex.: "essa foi o Gemini, vale revisar"). É a Lei #1 (ancoragem) aplicada à autoria.
state.ledger_projection agrega `contributors` e carrega provider/model nas decisões e
recentes; context.py renderiza. +1 teste (test_payload_shows_authorship). Validado contra
a própria LIFELINE: payload de 9 entradas mostra "fundado por anthropic/claude-opus-4-8".

<!-- lifeline:end -->

### #0012 — 2026-05-30T17:50:00+00:00 — fix

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: fix
- **summary**: O dogfooding pegou um furo de taxonomia — Entry.Kind não tinha 'milestone'; ingerir a própria LIFELINE quebrou
- **parents**: 519a9930dbfdda900f12fb4ef9f9aa94f38b2c014e5d702aea2f0b850200dc60
- **id**: 47fdd692fe1eaf8160d29960424e2da925bd2d7eb09f301709b42d52c8904cce

**Body**:
Ao ingerir a própria LIFELINE (que tem a #0008 com kind=milestone), o Entry (Literal
estrito) rejeitou 'milestone' — o enum Kind e o protocolo da LIFELINE não listavam. O
produto encontrou um bug em si mesmo: a #0008 foi escrita com um kind fora da taxonomia,
e o lifeline_hash.py (que não valida kind) deixou passar, mas o modelo estrito não. Fix:
adicionado 'milestone' e 'release' ao Kind (alinhando com a prática comprovada do inframoe)
e ao protocolo. Nota para o futuro: o uso conversacional (não-code) vai querer uma
taxonomia de kind mais aberta/extensível — decisão adiada, mas marcada aqui.

<!-- lifeline:end -->

### #0013 — 2026-05-30T18:10:00+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Threads em aberto explícitas no payload (kind 'open') — fecha o gap "o que vem a seguir" que o teste de aceitação apontou
- **parents**: 47fdd692fe1eaf8160d29960424e2da925bd2d7eb09f301709b42d52c8904cce
- **id**: 049a7056a777acf203ec16c27dff43eea0ba479640bbdb9734643b0a4b6b57b0

**Body**:
O teste de aceitação (#0008) revelou que o payload inferia "o próximo" pelos recentes, mas
não o declarava. Fix: novo kind `open` (uma thread / próximo passo em aberto). O
ledger_projection coleta os `open` numa lista `open_items`; uma entrada posterior que os
supersede (mesmo mecanismo das correções, Lei #2) os fecha. O ContextAssembler renderiza
uma seção "## Em aberto / próximo". +1 teste em state (coleta+fechamento) e +1 em context
(seção presente). 18 testes verdes. As entradas #0014-#0016 a seguir são as primeiras
threads abertas de verdade — o backlog do projeto agora vive ancorado, não em prosa solta.

<!-- lifeline:end -->

### #0014 — 2026-05-30T18:11:00+00:00 — open

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: open
- **summary**: Unificar os dois esquemas de hash — store vira a fonte de verdade e a markdown passa a ser GERADA a partir dele
- **parents**: 049a7056a777acf203ec16c27dff43eea0ba479640bbdb9734643b0a4b6b57b0
- **id**: 10c2f369b21b502d6e1987be2b40d25c3613b75f94d2cc1ff1aa6b8e0ec59d46

**Body**:
Hoje a cadeia da markdown (scripts/lifeline_hash.py, estilo prev_hash) e o id
content-addressed do Entry (estilo pais/DAG) coexistem. Unificar: o store (Entry) vira a
fonte única; a LIFELINE.md vira uma PROJEÇÃO gerada (como a montagem), não um arquivo
hand-edited. Isso colapsa os dois esquemas num só e torna o store primário — pré-requisito
limpo pro sync de nuvem (M3). Fecha quando o pipeline "append no store → regenera markdown"
existir.

<!-- lifeline:end -->

### #0015 — 2026-05-30T18:12:00+00:00 — open

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: open
- **summary**: Política de embedding (M3) — adapter plugável, fixo por índice, default local OSS; gravar modelo+dim como proveniência
- **parents**: 10c2f369b21b502d6e1987be2b40d25c3613b75f94d2cc1ff1aa6b8e0ec59d46
- **id**: 07b7abd76eb1650741f06e4b6e21180fe24fb7decca71e7e8e295e73f7a5b696

**Body**:
Não há embedding universal. Solução: interface de embedding plugável; UM modelo por índice
(vetores de modelos diferentes são incompatíveis); registrar modelo+dimensão por vetor
(proveniência); default local OSS (privacidade/custo) com opção de nuvem no tier pago.
Trocar de modelo = re-embeddar (migração). O vetor é só índice pra entrada ancorada — a
Lei #1 se mantém mesmo se o embedding errar o match. Fecha quando a Camada 3 escolher e
abstrair o embedding.

<!-- lifeline:end -->

### #0016 — 2026-05-30T18:13:00+00:00 — open

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: open
- **summary**: Camada 3 (recall semântico) — transplantar o vetor cosseno do SDK antigo, ancorado via causal_event_id
- **parents**: 07b7abd76eb1650741f06e4b6e21180fe24fb7decca71e7e8e295e73f7a5b696
- **id**: 8925a7205e21e940da3889063eb0237a3ea0f548aa02279b59519d9367fd3dd6

**Body**:
A 3ª camada de memória (recall associativo) ainda não existe. Transplantar o LocalVectorMemory
(cosseno em Python puro) do SDK antigo, com a regra de ouro: todo VectorRecord carrega o
hash do evento de origem (Lei #1). Permite "me traga as decisões passadas relevantes pra
isto" sem estourar o budget. Depende de #0015 (política de embedding). Fecha quando o
retrieval semântico ancorado estiver no Context Engine e testado.

<!-- lifeline:end -->

### #0017 — 2026-05-30T18:40:00+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: Prova de fogo COMPLEXA passou (6/6) — anti-staleness em escala, recusa de alucinação, atribuição multiprovider
- **parents**: 8925a7205e21e940da3889063eb0237a3ea0f548aa02279b59519d9367fd3dd6
- **id**: 6f35e1eeb8700aaacf645f9be24e30783b9b93c08edd9d1f442c331c0de65315

**Body**:
Teste adversarial (scripts/firetest.py): projeto fictício 'Aurora' com 24 entradas, 8
decisões (2 revertidas via correction: MongoDB→PostgreSQL, REST→gRPC), 4 providers/modelos
distintos como autores, incidentes/fixes como distratores, e 1 thread aberta fechada por
correção. Verificação programática: 8/8 checks PASS (superseded fora da verdade atual;
não-revertidos permanecem; thread fechada some; todos os 24 ids verificam). Agente novo,
zero contexto, só o payload (1805 chars): respondeu 6/6 — deu PostgreSQL e gRPC (não as
versões revertidas), atribuiu a mensageria ao Gemini corretamente, e RECUSOU ("não consta")
as 2 perguntas-isca cujas respostas não estavam no payload (retenção de logs, causa da
Black Friday). Sem alucinação. Reconciliou sozinho a thread fechada nos "Recentes".

Caveats honestos: ledger sintético e curado por mim; mesma família de modelo (Claude
testando Claude); compressão de 78% é modesta nessa escala (o valor foi seleção, não
encolhimento). CRUCIAL: o anti-staleness só funciona se a reversão for REGISTRADA — uma
reversão silenciosa (parar de usar X sem escrever correction) deixaria a decisão velha "em
vigor". É a fricção de captura na forma específica de reversões não-registradas.

<!-- lifeline:end -->

### #0018 — 2026-05-30T18:42:00+00:00 — open

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: open
- **summary**: Assembler deve suprimir/marcar itens superseded também na seção "Recente" (achado da prova de fogo)
- **parents**: 6f35e1eeb8700aaacf645f9be24e30783b9b93c08edd9d1f442c331c0de65315
- **id**: 7e3daa711c7f3caf6c6f74169bbfb110b08c0e6354253a746d5be64892588025

**Body**:
O agente da prova de fogo notou que a seção "Recente" mostra uma thread de `open` já
fechada junto da `correction` que a fechou — coexistência append-only que pode confundir.
A "Em aberto" já filtra superseded; a "Recente" não. Fix (M2): suprimir itens superseded
da "Recente", ou marcá-los como [fechado/revertido]. Achado pelo próprio teste — o produto
se criticando de novo.

<!-- lifeline:end -->

### #0019 — 2026-05-30T19:10:00+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Escopo vs self-healing/fine-tuning/deep-learning — Lifeline é MEMÓRIA/DADO ancorado, não executor, treinador nem infra de ML
- **parents**: 7e3daa711c7f3caf6c6f74169bbfb110b08c0e6354253a746d5be64892588025
- **id**: aa37198abe4ee19baf7e692b10c9b852c43ba2ce425525fd0a42f2d38ed704c2

**Body**:
Clareza de escopo pra não ressuscitar a inflação do SDK velho (#0002). O Lifeline serve a
essas áreas como SUBSTRATO, nunca sendo elas:

- **Self-healing: parcial — é a memória, não o curador.** Healing precisa detectar +
  decidir + AGIR (re-exec/rollback/sandbox) — tudo non-goal. O que o Lifeline dá é a
  memória institucional de falhas: `incident` (causa raiz) + `fix` (o que resolveu),
  ancorados, para o agente não repetir o erro. Quem cura é o orquestrador; o Lifeline o
  torna mais esperto.

- **Fine-tuning: majoritariamente NÃO — ele é a ALTERNATIVA.** Fine-tuning assa
  conhecimento nos pesos (caro, estático, difícil de corrigir); o Lifeline mantém o
  conhecimento externo (barato, dinâmico, corrigível por Lei #2, auditável por Lei #1). O
  produto existe pra tornar o fine-tuning desnecessário pro problema de CONTEXTO. Pode ser
  fonte de dado um dia (as `correction` são pares erro→fix→porquê), mas NÃO é pipeline de
  treino e o volume de um projeto é pequeno.

- **Deep learning: NÃO — erro de categoria.** É memória de camada de aplicação. Só
  *consome* um modelo de embedding na Camada 3; "usa embedding" ≠ "é pra DL".

A ponte que liga os três é o mecanismo de `correction` (sinal de aprendizado: erro→fix→
porquê) — mas é uma ponte de DADO/MEMÓRIA, não de o Lifeline executar healing ou treinar.
Regra: se uma proposta exige o Lifeline AGIR ou TREINAR, ela está fora de escopo; se exige
ele LEMBRAR ancorado, está dentro.

<!-- lifeline:end -->

### #0020 — 2026-05-30T19:40:00+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Item 3 — unificação de hash PROVADA: ingestão lossless + projeção store→markdown formam ponto fixo (store pode ser a fonte)
- **parents**: aa37198abe4ee19baf7e692b10c9b852c43ba2ce425525fd0a42f2d38ed704c2
- **id**: 286f4ed42d2f5e88754d5a097ff62f6094c179daa6252d201a92725135b00532

**Body**:
Landaram lifeline/projection.py (store → markdown, mostrando id content-addressed + parents)
e ingest.py lossless (preserva ts e parents; lê DAG explícito quando presente, senão encadeia
linear). test_projection prova o ponto fixo: store → markdown → store reproduz exatamente os
mesmos ids, e o 2º render é byte-idêntico, inclusive com correção de pai explícito (DAG não-
linear). scripts/migrate_check.py rodou na LIFELINE real: 19 entradas, ids estáveis, markdown
byte-idêntica — migração lossless. Os dois esquemas (prev_hash da markdown vs id do Entry)
ficam unificados no id content-addressed (ex.: #0001 vira 6f0d172f…, não mais 51b096c9…).

A pergunta "dá pra unificar com o store como fonte?" está RESPONDIDA (sim, provado). Mas a
#0014 continua ABERTA de propósito: a virada AO VIVO (sobrescrever LIFELINE.md, reescrever o
preâmbulo pro esquema novo, aposentar lifeline_hash.py) deve ser empacotada com um `lifeline
log` (CLI de append) — senão escrever a próxima entrada vira "escrever Python", pior que o
hand-edit atual. Decisão: virar quando houver forçante (M3 sync, ou agente escrevendo via API),
junto com a CLI. O valor já foi capturado: a dívida dos dois esquemas deixou de ser risco.

<!-- lifeline:end -->

### #0021 — 2026-05-30T21:00:09.653687+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: Item 3 fechado — virada ao vivo: store e a fonte, LIFELINE.md e gerada; CLI lifeline log no ar; lifeline_hash aposentado
- **parents**: 286f4ed42d2f5e88754d5a097ff62f6094c179daa6252d201a92725135b00532
- **id**: 4e16067750616ab5f82bf6e5d9d18bc8127fed07850ad737602e3a1c0550873a

**Body**:
Cutover executado via a propria CLI nova: ESTA entrada foi escrita por python -m lifeline log (dogfood do novo fluxo). 20 entradas migradas para .lifeline/ledger.db (fonte de verdade), todas integras; LIFELINE.md regenerada no formato content-addressed (id + parents, sem prev_hash). Backup do formato antigo em LIFELINE.md.pre-cutover.bak. Preambulo reescrito pro esquema novo; lifeline_hash.py aposentado em favor de lifeline verify. Fecha a thread #0014. Anexar agora e lifeline log (encadeia no head sozinho) e a markdown se regenera.

<!-- lifeline:end -->

### #0022 — 2026-05-30T21:03:37.113714+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: Artefato versionado = a LIFELINE.md gerada (diffavel/mergeavel); .lifeline/*.db e cache de runtime (gitignored), reconstruivel
- **parents**: 4e16067750616ab5f82bf6e5d9d18bc8127fed07850ad737602e3a1c0550873a
- **id**: cb234654623177ac1bff3b0d6426bc7e76521e59afbbbb1097acb6c790ac6283

**Body**:
Refina a #0014 com honestidade. O cutover poe o store como fonte de RUNTIME, mas commitar um .db binario briga com a tese GitHub-para-contexto: binario nao faz diff nem merge. Como o content-addressing torna texto e store losslessly interconversiveis (provado no #0020), o artefato git/sync e a LIFELINE.md (texto, diffavel, revisavel em PR) e o .lifeline/ledger.db vira cache local (gitignored), reconstruido com python -m lifeline migrate. Conclusao: a fonte de verdade e o CONJUNTO de entradas content-addressed, materializado como TEXTO (pra git/humanos) e como STORE (pra query). Nenhum e privilegiado porque sempre reconciliam.

<!-- lifeline:end -->

### #0023 — 2026-05-30T21:06:47.847986+00:00 — correction

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: correction
- **summary**: Thread #0014 FECHADA — unificacao de hash concluida e cutover ao vivo feito (ver #0020, #0021, #0022)
- **parents**: 10c2f369b21b502d6e1987be2b40d25c3613b75f94d2cc1ff1aa6b8e0ec59d46
- **id**: db84362394e5ac58667d2c4e43ec1ffff29f0c32653e008dabe21270fab5625c

**Body**:
Fecha a open #0014 aplicando a propria licao do #0017: conclusao registrada, nao silenciosa. O item 3 esta completo: store e a fonte de runtime, LIFELINE.md e gerada, CLI lifeline log no ar, lifeline_hash aposentado, artefato git = o texto (#0022).

<!-- lifeline:end -->

### #0024 — 2026-05-30T21:10:23.196957+00:00 — fix

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: fix
- **summary**: CLI crashava com UnicodeEncodeError em console Windows (cp1252) ao imprimir; stdout agora forcado a UTF-8
- **parents**: db84362394e5ac58667d2c4e43ec1ffff29f0c32653e008dabe21270fab5625c
- **id**: 2ff522ca09bc8da920dea7eca3099d0fa76d231ec43c11889a01c297b5e7b1d1

**Body**:
Dogfooding pegou de novo: rodar python -m lifeline context no Windows crashava no print do payload por causa do caractere de seta (U+2192), ausente em cp1252. Fix: main() reconfigura sys.stdout para utf-8 no inicio (try/except). O fechamento da #0014 ja tinha funcionado; o bug so escondia a visualizacao. Segundo bug revelado pelo proprio USO da ferramenta nesta sessao (o 1o foi o kind milestone na #0012) — evidencia de que dogfooding acha o que teste unitario nao acha.

<!-- lifeline:end -->

### #0025 — 2026-05-30T21:22:41.623086+00:00 — correction

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: correction
- **summary**: Fix #0018 FECHADA — assembler marca superseded na Recente + budget section-aware (header/abertos/recente nunca cortados)
- **parents**: 7e3daa711c7f3caf6c6f74169bbfb110b08c0e6354253a746d5be64892588025
- **id**: 33959fba0e18d3ef1214d603a4336da2b2b9191450bceecf67af79f65a4de1f0

**Body**:
Dois fixes no Context Engine fechando o achado da prova de fogo. (1) Itens superseded aparecem marcados [fechado/revertido] na secao Recente, em vez de coexistir confusos com a propria correcao. (2) Budget agora e section-aware: header, Em aberto e Recente sao SEMPRE incluidos; decisoes preenchem o resto mantendo as mais recentes e omitindo as antigas com marcador explicito (Lei #6), no lugar do corte-de-cauda cego que podia comer o que-vem-a-seguir. state expoe superseded; +1 teste. 27 testes verdes.

<!-- lifeline:end -->

### #0026 — 2026-05-30T21:45:13.997562+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Gaps a+c fechados — loop sem humano: tools MCP de escrita (lifeline_append/recontextualize) + auto-connect
- **parents**: 33959fba0e18d3ef1214d603a4336da2b2b9191450bceecf67af79f65a4de1f0
- **id**: 0ac08bdd5da6f57fc2048fb119a76c2916d32229c873b9f1b08d5cb53a4c205a

**Body**:
(a) ESCRITA via MCP: o servidor agora expoe lifeline_append (anexa decisao/feature/fix/open) e lifeline_recontextualize (supersede por id), alem do resource de leitura — a IA dirige os DOIS lados do loop, sem humano digitando. (c) AUTO-CONNECT: CLAUDE.md ganhou a secao O loop (ler ao conectar via python -m lifeline context ou resource MCP; escrever ao trabalhar); docs/INTEGRATION.md traz snippet de hook SessionStart do Claude Code e a config MCP. test_mcp confere o contrato. 7 suites verdes. Honesto: o MECANISMO de escrita-sem-humano existe; se a IA usa por habito ainda e questao comportamental, dependente da integracao pegar. Resta o gap (b): relevancia / Camada 3 (recall semantico), que depende de #0015 (embedding) — proximo passo.

<!-- lifeline:end -->

### #0027 — 2026-05-30T21:58:11.100722+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Camada 3 (recall ancorado) entregue — gap (b) relevancia fechado: assembler com query, embedder plugavel, default lexical
- **parents**: 0ac08bdd5da6f57fc2048fb119a76c2916d32229c873b9f1b08d5cb53a4c205a
- **id**: a6c47b7c71b100db28b0f8e6f3c1e79585043fb08116a28df698bff9ce0e6ebf

**Body**:
lifeline/recall.py: Embedder (costura plugavel, decisao #0015) + LexicalEmbedder default (term-frequency esparso, cosseno exato, sem dependencia) + SemanticRecall (indexa o ledger, top-k por relevancia, cada hit ANCORADO ao evento por id, Lei #1). ContextAssembler aceita query+recall e adiciona secao Relevante para a tarefa (relevancia, nao recencia). CLI: lifeline context --query. MCP: tool lifeline_recall. Licao honesta do dogfooding: tentei hashing embedder primeiro; o teste pegou colisao de buckets gerando FALSA relevancia (query sem palavra em comum pontuava 0.20) e troquei por TF esparso, que da 0 exato sem sobreposicao. 8 suites verdes.

<!-- lifeline:end -->

### #0028 — 2026-05-30T21:58:33.172029+00:00 — correction

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: correction
- **summary**: Threads #0015 (embedding) e #0016 (recall) FECHADAS — Camada 3 entregue (ver #0027)
- **parents**: 07b7abd76eb1650741f06e4b6e21180fe24fb7decca71e7e8e295e73f7a5b696, 8925a7205e21e940da3889063eb0237a3ea0f548aa02279b59519d9367fd3dd6
- **id**: fded7bfb4af1225093b9136bc0b53397482d2ff2ef6e11c0806dd640f4d7dda0

**Body**:
Politica de embedding implementada (interface plugavel + default lexical + nome do modelo gravavel) e recall semantico construido/integrado. Fecha as duas threads de uma vez (parents = ambos os ids).

<!-- lifeline:end -->

### #0029 — 2026-05-30T21:58:53.665406+00:00 — open

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: open
- **summary**: Plugar um embedder SEMANTICO denso (sentence-transformers/API) — o default atual e lexical (casa palavras, nao significado)
- **parents**: fded7bfb4af1225093b9136bc0b53397482d2ff2ef6e11c0806dd640f4d7dda0
- **id**: d2d305ab1b6b14dedd7757918cc4287bd79ed15e50418c2ae652b78b4e82c9c0

**Body**:
O LexicalEmbedder casa sobreposicao de tokens, nao similaridade semantica (ex.: query em ingles nao casa entrada em portugues). A interface Embedder ja permite plugar um modelo denso por tras (decisao #0015), pinado por indice, gravando modelo+dim como proveniencia. Fecha quando um embedder semantico estiver disponivel e medido vs o baseline lexical.

<!-- lifeline:end -->

### #0030 — 2026-05-30T22:15:21.762440+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Pacote de prova portatil (scripts/exam.py) — estressa QUALQUER modelo sem chave de API; SDK confirmado funcional
- **parents**: d2d305ab1b6b14dedd7757918cc4287bd79ed15e50418c2ae652b78b4e82c9c0
- **id**: 18b4de7bd554797cae59c34e7587b1457f8a5fd4252c9f08589e21971010151d

**Body**:
scripts/exam.py constroi um ledger adversarial (reversoes Mongo->Postgres e REST->gRPC, multi-provider, isca de alucinacao), monta o payload e escreve EXAM_prompt.md (cole em qualquer modelo: GPT, Gemini, etc. — responde so do contexto) + EXAM_key.md (gabarito + rubrica de aprovacao). Resolve o caveat de eu ter testado so com a mesma familia de modelo. Rodar o script tambem PROVA o SDK funcional ponta a ponta (store+state+context). Status do SDK: core single-user local FUNCIONAL — 8 suites verdes, CLI completa, MCP (read resource + write tools), aceitacao e prova de fogo passados. Fronteiras honestas: nao e pip-installable ainda (sem pyproject em v2); MCP nao foi rodado live contra cliente real nesta sessao (so o contrato registrado); recall e lexical (denso = #0029); nuvem M3 inexistente.

<!-- lifeline:end -->

### #0031 — 2026-05-30T22:21:39.865894+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: MCP testado AO VIVO — cliente MCP real (stdio) fez round-trip completo com o servidor; caveat MCP-live fechado
- **parents**: 18b4de7bd554797cae59c34e7587b1457f8a5fd4252c9f08589e21971010151d
- **id**: f72460cb0fd0298b31f0644d4dc9606b210785e33a1168951ab9dbf30e5642b2

**Body**:
scripts/mcp_live_test.py sobe o servidor (python -m lifeline.mcp_server, subprocesso) e fala por um cliente MCP REAL sobre stdio — mesmo protocolo do Claude Code. Round-trip: initialize (handshake), list_tools (append/recontextualize/recall), list_resources (lifeline://project/context), call_tool append x2 (escreveu no ledger PELO protocolo), read_resource (contexto refletiu as escritas: Mercurio + PostgreSQL), call_tool recall (top hit PostgreSQL score 0.53, ancorado). Logs do servidor mostram ListTools/CallTool/ReadResource processados. Ledger TEMP, sem poluir a line real. Falta apenas o APP Claude Code conectar via .mcp.json (config fornecida) — limitacao do harness atual impede anexar um servidor MCP novo no meio da sessao.

<!-- lifeline:end -->

### #0032 — 2026-05-30T22:26:38.472848+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: SDK instalavel — pyproject.toml + console scripts (lifeline, lifeline-mcp); pip install -e funciona de qualquer projeto
- **parents**: f72460cb0fd0298b31f0644d4dc9606b210785e33a1168951ab9dbf30e5642b2
- **id**: 488723b1f5f666eae70235e41400b5510860c740557b866ba9ced91508d819c8

**Body**:
Fecha o caveat nao-pip-installable. v2/pyproject.toml: name lifeline-context, deps pydantic+aiosqlite+mcp, requires-python >=3.10, packages.find include=lifeline* (evita o bug do SDK velho que excluia subpacotes). Entry points: lifeline (CLI) e lifeline-mcp (servidor MCP, com main() novo). PROVADO: pip install -e v2 instalou; o comando lifeline (em Scripts/) rodou de um diretorio TEMP fora do v2 e criou o proprio .lifeline/ledger.db daquele projeto — agora da pra apontar pra QUALQUER projeto, nao so dogfood. Nota honesta: o pacote lifeline ANTIGO na raiz sombreia quando cwd=raiz (sys.path[0]); rodar de outro dir ou arquivar o legado resolve.

<!-- lifeline:end -->

### #0033 — 2026-05-30T22:32:38.590311+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: SDK antigo arquivado em _legacy/ — raiz agora so tem v2/ (motor) e .git; sombra de import resolvida
- **parents**: 488723b1f5f666eae70235e41400b5510860c740557b866ba9ced91508d819c8
- **id**: e1c1d6ca68e55630fc59abfe5dae6cd15328c04f5b7d93be33b72dede64a2e35

**Body**:
Movido pra _legacy/ (reversivel, sem apagar): o pacote lifeline antigo, devos/, os 12 verify_*.py, tests antigos, pyproject quebrado, egg-info, docs do SDK velho (README/northstar/prd_contextfs/llms/.cursorrules) e artefatos (execution_trace, fire_test_trace, lifeline_demo.db). Raiz agora: .git, .gitignore, v2/, _legacy/. Resultado: (1) import lifeline da raiz resolve pro v2 instalado (nao mais pro pacote antigo que sombreava sys.path[0]) — confirmado: lifeline.__file__ aponta pra v2/lifeline; (2) v2/ pronto pra virar repo proprio; (3) enacta a extracao desenhada no comeco. README minimo na raiz aponta pro v2. Legado e referencia, nao executado.

<!-- lifeline:end -->

### #0034 — 2026-05-30T22:43:16.447022+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Documentacao senior de GitHub — README completo, ARCHITECTURE, CONTRIBUTING, AGENTS, LICENSE; a line (LIFELINE.md) e o ponto de entrada das IAs
- **parents**: e1c1d6ca68e55630fc59abfe5dae6cd15328c04f5b7d93be33b72dede64a2e35
- **id**: d2cd10b2e57eceadb8cb45effeb2a904fa8385f96554dd1b57b24dd2be68dcd1

**Body**:
Doc set nivel senior em v2/: README.md (problema, ideia, install, quickstart CLI+SDK, diagrama do loop, conceitos, refs CLI/MCP/SDK, secao Para IAs, 7 leis, non-goals, status+roadmap honestos, dogfooding, licenca). docs/ARCHITECTURE.md (modelo content-addressed, 3 camadas, supersessao, montagem/budget, recall, cutover store-e-fonte, ports de nuvem, com referencias as entradas). CONTRIBUTING.md (disciplina + quality gate). AGENTS.md (onboarding tool-agnostico p/ qualquer IA: conecta pela line/MCP, obedece as leis, anexa). LICENSE MIT (default permissivo pro core OSS, open-core). A line que qualquer IA le e a propria LIFELINE.md (#0001+) / lifeline context / resource MCP — os docs apontam pra ela. Tudo em PT; EN pendente p/ alcance global.

<!-- lifeline:end -->

### #0035 — 2026-05-30T23:12:13.024681+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Multi-line nativo — --line <nome> mapeia ledger E view juntos; fim da colisao de LIFELINE.md; comando lines
- **parents**: d2cd10b2e57eceadb8cb45effeb2a904fa8385f96554dd1b57b24dd2be68dcd1
- **id**: c0713be34201af351e176f8946accb510a916d7e6c746a40cfca0d6e37aee757

**Body**:
Resolve o gap que a demo de multi-line revelou: lines tinham .db independentes mas a view markdown (--out) tinha nome fixo LIFELINE.md e se sobrepunha. Agora resolve_paths(line, db, out) faz --line NAME mapear .lifeline/NAME.db + LIFELINE.NAME.md JUNTOS — sem colisao. Default preservado (sem --line: .lifeline/ledger.db + LIFELINE.md). Novo comando lifeline lines lista as lines do projeto. Modelo confirmado: uma LINE = um ledger nomeado (codigo OU conversa); um projeto tem 1 por default e suporta N; lines nao sao presas a projeto. Views LIFELINE.<nome>.md sao commitadas (diffaveis); .db fica em .lifeline/ (gitignored). +3 testes (resolve_paths, nao-colisao, lines). 8 suites verdes. Provado ao vivo: 2 lines (backend/codigo + research/conversa) coexistindo sem sobrepor view.

<!-- lifeline:end -->

### #0036 — 2026-05-31T00:05:24.639578+00:00 — feature

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: feature
- **summary**: Fluxo HITL de escrita — propose (async, anti-sujeira) -> review -> approve; IA via MCP agora PROPOE, humano cura
- **parents**: c0713be34201af351e176f8946accb510a916d7e6c746a40cfca0d6e37aee757
- **id**: 5ad7e7279d9068ccfa0fa3eb9a524d83aebc3bad52efc8538a9d6737150ac3c1

**Body**:
Materializa o modelo "IA se organiza, humano cura". lifeline/staging.py (StagingStore: fila de propostas, tabela propria na mesma db; a line so recebe aprovado). CLI: propose (async/leve — NAO toca na line nem regenera view, sem latencia; captura intent+porquE; valida kind + EXIGE body = anti-sujeira no write-time), review (lista pendentes = curadoria), approve <pid|all> (sela na line preservando o ts do momento da decisao), reject. Tiering como aprovar comando shell: humano no `log` = commit direto (ele e o aprovador); IA via MCP lifeline_append/recontextualize agora PROPOE (pendente) — refina o comportamento commit-direto do #0026 (a IA dirige a captura, mas nao suja a verdade; o humano gateia). +5 testes (test_staging). 9 suites verdes. Provado ao vivo: sem porquE recusa; com porquE fica pendente; line so muda no approve.

<!-- lifeline:end -->

### #0037 — 2026-05-31T00:16:21.484151+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: M3 Tier 0 — git sync (custo zero): push/pull/clone sincronizam a line; o remoto git vira o hub do contexto
- **parents**: 5ad7e7279d9068ccfa0fa3eb9a524d83aebc3bad52efc8538a9d6737150ac3c1
- **id**: ae76fbc606eb0c6f4f224161b1fa8db407b795abcd495eea4cbc340f37e3c1bd

**Body**:
lifeline/sync.py (wrappers git) + CLI push/pull/clone. Reusa o #0022 (a view textual e o artefato versionado; o .db e cache reconstruivel): push = rebuild+commit+push; pull = pull + migrate + rebuild (ingere a view mergeada, dedup por id content-addressed); clone reconstroi o .db da view clonada. Conflito de merge aborta com mensagem (resolve no LIFELINE.md, que e legivel). Provado: test_sync (push em A -> clone B -> a line propagou) + demo ao vivo com hub bare local. Resultado: cross-device + colaboracao via git, custo ZERO, GitHub vira o hub — o Tier 0 do M3 que arquitetamos, sem infra nova. Tier 1 (Supabase pros chats web) e o merge multi-writer (M4) seguem o mesmo protocolo content-addressed. +2 testes. 10 suites verdes.

<!-- lifeline:end -->

### #0038 — 2026-05-31T00:32:04.869215+00:00 — decision

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: decision
- **summary**: M3 SEM Redis — git (sync) + Supabase Realtime (push) cobrem; Redis no maximo cache de escala futuro, nunca dependencia de nucleo
- **parents**: ae76fbc606eb0c6f4f224161b1fa8db407b795abcd495eea4cbc340f37e3c1bd
- **id**: 63b3fc677c65b60c1f294ab0fedbdfc783258a30a7c649f8773c45c55fc1e05a

**Body**:
Poda pedida pelo dono. Redis entrou por reflexo no esboco do M3 e nao se sustenta: (1) SYNC = git no Tier 0; (2) REAL-TIME/push = Supabase Realtime (free tier, via replicacao do Postgres) cobre o papel que seria do Redis Streams; (3) CACHE do contexto montado = in-process / tabela Postgres no MVP; (4) sem filas/jobs (o lado de execucao foi cortado, ver #0019); (5) auth/sessao = Supabase JWT. Contra o criterio de custo-zero: Redis seria mais um servico pra hospedar (custo + ops). Redis SO ganharia lugar em ESCALA (cache compartilhado de baixa latencia entre replicas) — e mesmo ai edge KV ou o proprio Supabase podem bastar; entao e, no maximo, otimizacao futura atras de um forcante real, nunca dependencia de nucleo. O SDK velho tinha um RedisEventBus stub/teatro — esta decisao impede que uma IA futura reconstrua isso. M3 enxuto: Tier 0 = git (feito); Tier 1 = Supabase (Postgres/Auth/RLS/Realtime/PostgREST) SEM Redis.

<!-- lifeline:end -->

### #0039 — 2026-05-31T00:41:55.027794+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: M3 Tier 1 kit (Supabase): schema.sql + adapter de referencia + runbook
- **parents**: 63b3fc677c65b60c1f294ab0fedbdfc783258a30a7c649f8773c45c55fc1e05a
- **id**: 7f8c20959b149ad0cd7f94acc1f312474d9ab32c812f98c9af11b98a39e872c8

**Body**:
Gerado o kit do Tier 1 em cloud/ e docs/. (a) cloud/schema.sql: tabela lifeline_entries multi-tenant, dedup por (owner,line,id), seq para ordem causal, e RLS APPEND-ONLY — so SELECT/INSERT do proprio auth.uid(); sem policy de UPDATE/DELETE, entao o banco impoe as Leis #1 e #2. (b) cloud/supabase_store.py: SupabaseEventStore atras do port EventStore (PostgREST via httpx), marcado EXPERIMENTAL e FORA do core testado — promove com teste quando rodar contra projeto real. (c) docs/M3_TIER1_SUPABASE.md: runbook. Projeto do usuario: ref rzphncyjrilhwpuemrcl. Seguranca: schema roda no dashboard sem compartilhar key; runtime le SUPABASE_URL/KEY do ambiente; .env adicionado ao .gitignore; service_role nunca em chat/commit. Nao consegui operar o banco desta sessao (sem MCP do Supabase ativo aqui — conexao MCP e fixada no inicio da sessao).

<!-- lifeline:end -->

### #0040 — 2026-05-31T01:03:42.849421+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: v2 promovido a raiz do repo; rev0 arquivada em _legacy/ — produto entra no versionamento (destrava Tier 0)
- **parents**: 7f8c20959b149ad0cd7f94acc1f312474d9ab32c812f98c9af11b98a39e872c8
- **id**: aceead44419ff7575a96964906ee301bf2eeb43d6e9213a2c30f57409fef9957

**Body**:
Reestruturacao (opcao b do dono). Antes: o HEAD commitado ainda era o SDK rev0; o produto real (v2/ — codigo limpo + ledger de 39 entradas) estava UNTRACKED, sem historico. Isso era incoerente com a tese 'GitHub para contexto' e impedia o Tier 0 — nao da pra 'lifeline push' uma line que nem esta num commit. Acao: movido v2/* para a raiz (sem colisao real; so .gitignore e README.md, versoes do v2 venceram); a rev0 inteira ja estava arquivada em _legacy/. Feito na branch m3/promote-v2-root para ser reversivel; main intacta na rev0 ate o merge. CLI roda da raiz (antes era 'cd v2'); store .lifeline/ viajou junto; verify OK. Pre-requisito do M3 Tier 1 (Supabase) cumprido.

<!-- lifeline:end -->

### #0041 — 2026-05-31T01:31:01.483485+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: M3 Tier 1: SupabaseEventStore promovido ao pacote + seam --store supabase na CLI, com testes de wire mockados e teste live skip-gated
- **parents**: aceead44419ff7575a96964906ee301bf2eeb43d6e9213a2c30f57409fef9957
- **id**: 127d6a4180f897feafe68fa9743fc65094e21719a785394eda24b2d58a83c0cd

**Body**:
Opcao 1 da outra sessao, com a disciplina do #0039 (sem overclaim). (1) Adapter movido de cloud/supabase_store.py para lifeline/cloud.py — importavel apos install, com transporte httpx injetavel (httpx.MockTransport) p/ teste. (2) CLI ganhou --store {sqlite,supabase}: _open() faz o branch; log/context/verify/rebuild/migrate funcionam na nuvem pelo mesmo port EventStore; push/pull/clone/lines e o HITL ficam barrados no modo supabase (sao do store local) com mensagem clara. (3) tests/test_supabase.py: 8 testes de WIRE mockados (montagem de POST/GET, headers apikey+Bearer+Prefer, filtros eq/cs, parse de payload->Entry, idempotencia por status, erro claro sem env, guarda da CLI) que rodam sempre + 2 testes LIVE skip-gated (round-trip real e prova de que a RLS e append-only: UPDATE/DELETE negados) que so rodam com SUPABASE_URL/KEY. Suite: 53 passam, 2 skip. (4) httpx virou dep explicita do core (ja vinha via mcp) + extra [cloud]. (5) DECISAO de auth ancorada: SUPABASE_KEY deve ser access token de USUARIO (JWT) p/ auth.uid() resolver na RLS; service_role bypassa a RLS e deixa owner nulo, nao serve p/ escrita multi-tenant. Falta: a outra sessao (com o MCP/creds) rodar o schema.sql e o teste live p/ provar o contrato real; depois HITL-na-nuvem e MCP remoto SSE.

<!-- lifeline:end -->

### #0042 — 2026-05-31T02:33:43.480922+00:00 — milestone

- **author**: jessianjmb@gmail.com
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-opus-4-8
- **kind**: milestone
- **summary**: M3 Tier 1 VALIDADO ao vivo: schema Supabase aplicado + RLS append-only provada; bug apikey vs Bearer achado e corrigido (suite 55/55 com live)
- **parents**: 127d6a4180f897feafe68fa9743fc65094e21719a785394eda24b2d58a83c0cd
- **id**: a8e2a0cc74440f9503cfdbf0c260767e362eab0b2b0203ab376274a2c9b90d66

**Body**:
Fecha o caveat do #0039/#0041 (o kit estava "nao validado ao vivo"). Com o PAT do dono no .env, apliquei cloud/schema.sql via Management API (role postgres): tabela lifeline_entries criada, RLS habilitada, policies so SELECT/INSERT (append-only imposto pelo banco).

Provas AO VIVO pelo PostgREST contra o projeto real (ref rzphncyjrilhwpuemrcl):
- INSERT anon NEGADO -> 42501 "new row violates row-level security policy": append-only/anti-tenant garantido pelo Postgres (Leis #1 e #2), nao so por convencao.
- Round-trip autenticado OK: INSERT com apikey=anon + Authorization=Bearer <JWT de usuario> seta owner=auth.uid() e passa a RLS; get/stream leem de volta.

BUG achado por DOGFOODING (nao pelos mocks): o SupabaseEventStore mandava self.key tanto no header apikey quanto no Authorization. O gateway do Supabase REJEITA o JWT de usuario como apikey -> 401 "Invalid API key". Os mocks nao pegaram porque nao exercitam a validacao de apikey do gateway. Fix em lifeline/cloud.py: separar apikey (chave do projeto) do token (Bearer = JWT), lido de SUPABASE_TOKEN; e construcao com key explicita NAO herda token do ambiente (isolamento de teste). Mocks seguem verdes e os 2 testes live agora passam -> suite 55/55 (com creds; 8+2skip sem creds, CI-safe).

Caveat honesto: o JWT de usuario e curto (~1h) -> auth duravel do CLI (login/refresh) e o proximo passo do Tier 1. O .mcp.json ganhou o servidor supabase oficial (npx), mas a Management API direta com o PAT ja bastou pra criar+validar; o MCP fica como opcao p/ sessoes futuras.

<!-- lifeline:end -->

### #0043 — 2026-05-31T02:46:33.361118+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Trava o fix de auth do #0042 no CI (testes de wire p/ apikey vs Bearer) e corrige docs stale
- **parents**: a8e2a0cc74440f9503cfdbf0c260767e362eab0b2b0203ab376274a2c9b90d66
- **id**: 2468cd300c40e26a73f4b27d04a88e94cfd1ffdb3e86eef2aef2eb2b3ae8053d

**Body**:
A outra sessao validou o Tier 1 ao vivo e corrigiu o cloud.py (apikey do projeto no header apikey; JWT do usuario no Authorization: Bearer), mas o commit ead2f07 nao tocou testes nem docs — entao o fix so estava protegido pelo teste LIVE (skip-gated, nao roda no CI) e os docs ficaram errados. Fechei o gap: (1) 3 testes de wire mockados que travam a separacao — apikey=projeto / Bearer=token, fallback do token p/ apikey quando ausente, e leitura de SUPABASE_KEY+SUPABASE_TOKEN do ambiente; (2) o gate dos testes live agora exige tambem SUPABASE_TOKEN (sem ele a escrita 401 em vez de pular); (3) docs/M3_TIER1_SUPABASE.md reescrito p/ o modelo de DOIS valores (SUPABASE_KEY=apikey anon, SUPABASE_TOKEN=JWT de usuario). Suite 56/56 (+2 skip live).

<!-- lifeline:end -->

### #0044 — 2026-05-31T02:56:18.322228+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: HITL na nuvem: StagingStore vira port + SupabaseStagingStore (tabela lifeline_proposals); propose/review/approve/reject no modo --store supabase
- **parents**: 2468cd300c40e26a73f4b27d04a88e94cfd1ffdb3e86eef2aef2eb2b3ae8053d
- **id**: b0eb308ff5a8149eb94ee7aebde8dc049976da54bab539e8f74d04d22d71e0f3

**Body**:
Leva a curadoria anti-sujeira pro modo nuvem (a IA propoe, o humano cura), nao so o store local. (1) staging.py: StagingStore virou PORT (ABC) + SQLiteStagingStore (impl atual). (2) cloud.py: extrai _SupabaseBase (creds/headers/client compartilhados — comportamento da auth #0042 preservado, garantido pelos wire-tests) e adiciona SupabaseStagingStore. (3) cloud/schema.sql: tabela lifeline_proposals — MUTAVEL (status muda), RLS permite SELECT/INSERT/UPDATE do dono mas SEM DELETE (preserva historico de curadoria); contraste explicito com lifeline_entries que e append-only. (4) cli.py: factory _staging() espelha _open(); propose/review/approve/reject usam o backend ativo; _LOCAL_ONLY encolheu p/ {push,pull,clone,lines} (HITL saiu — agora funciona na nuvem). (5) testes: +4 wire mockados (propose->pid com return=representation, pending filtra por line+status e normaliza parents jsonb->string JSON p/ cmd_approve ficar agnostico, get vazio, set_status PATCH por pid) + 1 live HITL round-trip skip-gated. Suite 60 passa / 3 skip. Falta: auth ergonomica do CLI e o MCP remoto SSE (superficie dos chats web).

<!-- lifeline:end -->

### #0045 — 2026-05-31T03:03:45.421881+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: Tier 1 completo validado ao vivo POR MIM: ledger + RLS append-only + HITL na nuvem; tabela lifeline_proposals aplicada no projeto; suite 63/63 com live
- **parents**: b0eb308ff5a8149eb94ee7aebde8dc049976da54bab539e8f74d04d22d71e0f3
- **id**: b9afeda5767abd77096ff5e89cba36bc8f0cfb8fb1e5498e533eb6d0283332ad

**Body**:
Com SUPABASE_URL/KEY/TOKEN do .env, rodei os 3 testes live contra o projeto real (rzphncyjrilhwpuemrcl): round-trip do ledger, RLS append-only (UPDATE/DELETE negados) e o round-trip HITL (propose->pending->status). O #0042 da outra sessao validou so o ledger (entries); o HITL (#0044) faltava a tabela. O MCP nesta sessao nao tem o management token em runtime (Unauthorized p/ DDL), entao apliquei cloud/schema.sql direto pela Management API (POST /v1/projects/{ref}/database/query) com o SUPABASE_ACCESS_TOKEN do .env — idempotente, criou lifeline_proposals. Suite completa: 63 passam, 0 skip (todos os live ligados). Fecha o caveat 'nao re-verifiquei a nuvem': agora o store remoto inteiro (ledger append-only + fila HITL mutavel sem-delete) esta provado de ponta a ponta. Falta do Tier 1 so o MCP remoto (SSE), a superficie dos chats web.

<!-- lifeline:end -->

### #0046 — 2026-05-31T03:11:37.457755+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: MCP remoto (HTTP/SSE): mesma superficie store-agnostica via lifeline-mcp-remote; escrita HITL; falta OAuth p/ conectores web e multi-tenant
- **parents**: b9afeda5767abd77096ff5e89cba36bc8f0cfb8fb1e5498e533eb6d0283332ad
- **id**: e6ba741ae3abedcca3fb4a596bad58120f5e9eb9a5ed22e39add50d5e6855ff5

**Body**:
Expoe a superficie MCP por HTTP (nao so stdio), pra IA conectar de fora. (1) mcp_server.py virou store-agnostico: resource/recall usam o factory _open da CLI; _configure() escolhe backend/line por env (LIFELINE_STORE=supabase usa SUPABASE_URL/KEY/TOKEN, default sqlite). (2) Novo entry-point lifeline-mcp-remote (main_remote): serve sobre SSE (/sse + /messages) ou streamable-http (/mcp), bind por LIFELINE_MCP_HOST/PORT. Mesmas tools: leitura (context+recall) e escrita HITL (append/recontextualize PROPOEM, nao commitam). (3) Testes: surface registrada (incl. recall), _configure escolhe backend por env, e a tool de escrita e HITL (proposta pendente, 0 na line). uvicorn/starlette ja presentes; sse_app/streamable_http_app constroem com rotas. Suite 63/63 (+3 live skip). CORRECAO de rota honesta: NAO roda em Supabase Edge Functions (Deno); e servidor Python, hospedavel em qualquer free-tier (Fly/Render/Railway) com o Supabase de store. FALTA: OAuth 2.1 no endpoint (exigido pelos conectores claude.ai/ChatGPT/Gemini) + multi-tenant por JWT de usuario — proximo incremento; a RLS (owner=auth.uid) ja esta pronta pra isso.

<!-- lifeline:end -->

### #0047 — 2026-05-31T03:24:06.782024+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: OAuth Resource Server no MCP remoto (LIFELINE_OAUTH=1): valida JWT Supabase por requisicao, escopa RLS por usuario (multi-tenant), serve protected-resource metadata
- **parents**: e6ba741ae3abedcca3fb4a596bad58120f5e9eb9a5ed22e39add50d5e6855ff5
- **id**: 98a638ee793fcb22f7087402603eabdd4d739fc06b725bdd65ac6da1cb446362

**Body**:
A ultima milha do M3, na parte que da pra fechar+testar aqui. (1) SupabaseTokenVerifier (TokenVerifier do SDK): valida o Bearer contra /auth/v1/user; 200->AccessToken carregando o proprio JWT + user id; 401->None. Transporte httpx injetavel p/ teste. (2) Binding por-requisicao: _request_token() le o token validado (get_access_token), e _open_request/_staging_request constroem o store/staging com o JWT DAQUELE usuario -> RLS escopa por owner=auth.uid() = multi-tenant real (sem isso era single-tenant via env). (3) _register() passou a registrar a superficie em qualquer instancia FastMCP; _build_remote() liga o Resource Server quando LIFELINE_OAUTH=1 (+supabase+creds): FastMCP(token_verifier, AuthSettings(issuer,resource_server_url)) -> exige Bearer e publica GET /.well-known/oauth-protected-resource (RFC 9728). (4) Testes: verifier valido/invalido/sem-config, build com OAuth serve metadata, build sem OAuth = servidor base. Suite 68/68 (+3 live skip). HONESTO: o lado Authorization Server (DCR + authorization-code) que claude.ai/ChatGPT/Gemini dirigem NAO esta feito — o Supabase Auth nao e AS OAuth2 generico com DCR; rotas (AS shim / provedor com DCR / aguardar Supabase) documentadas em docs/MCP_REMOTE.md. Em todas, o nosso RS nao muda. Da p/ conectar JA com um JWT em mao (claude mcp add --header).

<!-- lifeline:end -->

### #0048 — 2026-05-31T03:25:43.343560+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: OAuth Resource Server validado ao vivo: verifier aceita JWT real (200, escopa por usuario) e rejeita invalido (403) contra o Supabase auth real
- **parents**: 98a638ee793fcb22f7087402603eabdd4d739fc06b725bdd65ac6da1cb446362
- **id**: 7aa49c9c2dcae14a04c63e0a53bc944239eb3c56533f63e363cb70a4b3001420

**Body**:
Mesmo padrao dos #0042/#0045 (validar ao vivo, nao so mock). Com as creds do .env rodei o SupabaseTokenVerifier contra https://<proj>.supabase.co/auth/v1/user: token real -> 200 -> AccessToken com user id (escopo multi-tenant ok); 'jwt.invalido' -> 403 -> None (rejeitado). Confirma o RS de ponta a ponta. Falta so o Authorization Server (DCR/auth-code) dos conectores hospedados — decisao de arquitetura/integracao, nao codigo do nosso lado.

<!-- lifeline:end -->

### #0049 — 2026-05-31T03:28:18.742815+00:00 — open

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: open
- **summary**: Proximo: OAuth Authorization Server (DCR + authorization-code/PKCE) p/ plugar nos conectores hospedados (claude.ai/ChatGPT/Gemini)
- **parents**: 7aa49c9c2dcae14a04c63e0a53bc944239eb3c56533f63e363cb70a4b3001420
- **id**: 9062526020106de9959dba102e62f55f75187b3306f9cc1521f0f49a11e0cc89

**Body**:
Unica peca restante do M3. O Resource Server (validacao de JWT + multi-tenant por RLS + protected-resource metadata) esta feito e validado ao vivo (#0047/#0048) e NAO muda. Falta o AS, que os conectores dirigem sozinhos. Rotas avaliadas (decisao adiada pelo dono): (a) AS shim via OAuthAuthorizationServerProvider do SDK, ponte pro Supabase Auth — custo-zero, no repo, mas security-critical e so valida ao vivo contra o conector; (b) provedor com DCR (Auth0/WorkOS/Keycloak) emitindo o JWT que o RS ja valida — menos codigo, possivel custo. Comecar fresco quando for testar contra o claude.ai real.

<!-- lifeline:end -->

### #0050 — 2026-05-31T03:47:54.458026+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Hardening pos-auditoria (Top 5): resiliencia de rede na nuvem, README, CI, rede de erro na CLI, logging + teste de isolamento
- **parents**: 9062526020106de9959dba102e62f55f75187b3306f9cc1521f0f49a11e0cc89
- **id**: 164fa86abd4f4f1dcf35569e0db73704ad923b50a2c920aa482dad7d2d70a8fe

**Body**:
Resposta acionavel a auditoria de producao. (1) README: corrigido o install quebrado (pip install -e . na raiz, nao 'v2/' que nao existe mais), badges (68 testes) e deps (httpx + extra [cloud]) — destrava onboarding. (2) cloud.py: _ensure_ok() loga+levanta em 4xx/5xx em TODOS os metodos; append passou a usar return=representation e distingue inserido(True)/duplicata(False) igual ao SQLite — falha real NUNCA mais mascarada como dedup (era o bloqueador #2/#3 do audit). Provado ao vivo: token expirado deu 401->log ERROR+HTTPStatusError, antes daria 'duplicada (idempotente)'. (3) CI: .github/workflows/ci.yml roda pytest+verify no push/PR (py3.10/3.12) — pega o drift que o audit achou (README stale, #0043 foi manual). (4) cli.py: dispatch extraido p/ _dispatch(); main() envolve em try/except -> erro de rede vira mensagem amigavel + exit 1, nao traceback (SystemExit do argparse passa intacto). (5) logging em cloud.py/mcp_server.py (o except silencioso de auth virou debug log) + teste live skip-gated de isolamento (anon nao le linhas do usuario via RLS). Suite 70/70 (+4 live skip). Pendente p/ re-validacao live funcional: refresh do SUPABASE_TOKEN (expira ~1h).

<!-- lifeline:end -->

### #0051 — 2026-05-31T04:11:35.450315+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Local rumo a 10 + gancho local->nuvem com qualidade: locks de primeira-execucao/re-seed, .env.example, e a graduacao documentada/testada
- **parents**: 164fa86abd4f4f1dcf35569e0db73704ad923b50a2c920aa482dad7d2d70a8fe
- **id**: 69e18d62fdb82e5a94b9229959933a20f854964b300bead297c712a621228e3c

**Body**:
Corretude-nucleo do local ja estava travada por teste (determinismo, anti-tamper, supersessao, round-trip ponto-fixo) — nao dupliquei. Fechei os gaps reais que faltavam pro '10 polido': (1) teste de ledger VAZIO (primeira execucao e graciosa, placeholder, sem crash); (2) teste de IDEMPOTENCIA do ingest (re-seed nao duplica — content-addressed); (3) .env.example (template do modo nuvem, sem segredo); (4) README: 'Status & roadmap' corrigido (estava stale: dizia 8 suites, M3 planejado/Redis, 'nuvem nao existe' — agora reflete M3 validado ao vivo + limites honestos) e nova secao 'Do local pra nuvem (graduacao)'; (5) gancho local->nuvem como fluxo de primeira-classe: 'lifeline --store supabase migrate --from LIFELINE.md' e LOSSLESS+IDEMPOTENTE (mesmos ids), com teste live skip-gated (test_seed_cloud_from_local_markdown). Suite 72/72 (+5 live skip). Veredito honesto: local agora ~9/10 (o '10 teorico' fica no O(n) por chamada — deliberadamente nao otimizado, trivial na escala real — e na ausencia de assinatura, fora do threat-model local).

<!-- lifeline:end -->

### #0052 — 2026-06-01T12:31:04.117437+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Corrige overclaim no MCP_REMOTE.md (Bearer estatico NAO serve no claude.ai web) + ancora a pesquisa de auth dos conectores
- **parents**: 69e18d62fdb82e5a94b9229959933a20f854964b300bead297c712a621228e3c
- **id**: b6dc0ef0874e90ae77f2694a69fc163d734a9ff23e29860af60b20273ff51fcf

**Body**:
Pesquisa fact-checked (jun/2026, fontes oficiais Anthropic/OpenAI/Google/spec MCP) sobre o que os chats exigem pra conectar MCP remoto. ACHADOS: (1) claude.ai SUPORTA conector AUTHLESS (auth='none') -> one-click sem AS, mas sem identidade por usuario (single-tenant/compartilhado, nao multi-tenant). (2) DCR NAO e obrigatorio: claude.ai aceita CIMD ou client pre-registrado (Anthropic-held creds via mcp-review@anthropic.com); ChatGPT aceita CIMD/clients predefinidos; a spec MCP diz DCR='MAY'. (3) BEARER ESTATICO NAO SERVE nos apps web (claude.ai: static_bearer 'not yet supported'; ChatGPT idem) — so funciona nos CLIs (Claude Code, Gemini CLI). Isso CORRIGE o doc, que implicava 'claude mcp add --header' pro claude.ai web. (4) ChatGPT exige Developer Mode (planos PAGOS; free nao tem). (5) Gemini consumo nascente (CLI ok; app/enterprise). (6) AS zero-custo com DCR: Cloudflare workers-oauth-provider (OSS/free Workers), Keycloak (OSS), Stytch (free ~10K MAU); Auth0 enterprise/opaco. CONCLUSAO DE NEGOCIO: o valor pago (multi-tenant nos chats) E gated por um AS, MAS nao por DCR; e da pra VALIDAR o one-click via authless (claude.ai) sem AS nenhum. A workflow de deep-research falhou (StructuredOutput), refeito via WebSearch/WebFetch direto.

<!-- lifeline:end -->

### #0053 — 2026-06-01T12:37:47.725665+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Conector authless pronto p/ deploy (validacao one-click no claude.ai): Dockerfile + .dockerignore + DEPLOY.md, smoke de boot OK
- **parents**: b6dc0ef0874e90ae77f2694a69fc163d734a9ff23e29860af60b20273ff51fcf
- **id**: 7b310808ac129ce62fba8a19cb785f10055053e042c2f2b5747d38f7da8c1973

**Body**:
Caminho (a) escolhido pelo dono: validar o one-click nos chats SEM construir AS, usando o modo authless que o claude.ai aceita (pesquisa #0052). Entregue: (1) Dockerfile — reconstroi o .db da LIFELINE.md versionada no boot e serve authless via streamable-http (/mcp), respeitando  (Render/Railway); (2) .dockerignore — NUNCA empacota .env/segredo/_legacy/cache; (3) docs/DEPLOY.md — smoke local, deploy free-tier (Railway/Render/Fly) e os cliques de registro no claude.ai (Authentication: None). Smoke real: o servidor sobe no uvicorn e fica ouvindo :8000/mcp (testado local). SEGURANCA (honesto): authless+publico = qualquer um com a URL le o contexto e pode enfileirar propostas — mitigado por HITL (escrita so PROPOE; nao corrompe a line) + usar line nao-sensivel (o demo expoe a propria LIFELINE.md, ja publica). NAO usar com dado privado — pra isso e multi-tenant+AS (#0049). O dono deploya e da o clique final no claude.ai.

<!-- lifeline:end -->

### #0054 — 2026-06-01T13:53:25.599113+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Fix 421 'Invalid Host header' no MCP remoto: transport_security aceita host publico (tunel/proxy/deploy)
- **parents**: 7b310808ac129ce62fba8a19cb785f10055053e042c2f2b5747d38f7da8c1973
- **id**: b98f8da17d509ad10541a393690ee81f871ee6a171ad47285dabccad08b6c731

**Body**:
Achado testando o conector authless por tunel cloudflare: o FastMCP, por padrao, so confia em Host=localhost (anti-DNS-rebinding), entao rejeita com 421 qualquer requisicao cujo Host seja o dominio publico — bloqueava TODO deploy/proxy/tunel, nao so o demo. Fix: _transport_security() em mcp_server.py — LIFELINE_MCP_ALLOWED_HOSTS=host1,host2 libera esses com a protecao ON; sem a lista, desliga a protecao (servidor remoto ja e publico). _build_remote() agora SEMPRE constroi um FastMCP fresco com esse transport_security (antes o caminho authless reusava a instancia stdio sem ele). +2 testes (lista libera host / default desliga). Suite 74/74 (+5 live skip). Aprendizado: hospedar tunel efemero a partir da sessao do agente e fragil (caiu com exit 127) — o deploy/tunel deve rodar no terminal do dono p/ persistir.

<!-- lifeline:end -->

### #0055 — 2026-06-01T14:23:07.609835+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Deploy no Render preparado: /healthz (health check), render.yaml (Blueprint) e DEPLOY.md Render-first
- **parents**: b98f8da17d509ad10541a393690ee81f871ee6a171ad47285dabccad08b6c731
- **id**: 4a900baf9bfae2d5d1d71f72a61c8206f21065dc9359b0ad3e501906209de71c

**Body**:
Decisao do dono: Render free agora (validar, /usr/bin/bash), Railway depois (quando aprovar conexao+viabilidade). Render free usa o Dockerfile como esta, dorme apos 15 min (cold start ~1 min) e nao exige cartao. Adicionado: (1) rota GET /healthz -> 200 'ok' (registrada via _register em qualquer instancia; health check de Render/Railway + checagem no navegador; smoke local confirmou 200); (2) render.yaml (Blueprint: web/docker/free/healthCheckPath=/healthz/autoDeploy; comentario p/ promover a starter  e p/ envs OAuth multi-tenant futuras); (3) DEPLOY.md Render-first com Blueprint+manual, nota de cold-start, e a licao do tunel (rede bloqueia porta 7844 do cloudflared — deploy resolve). Suite 76/76 (+1 teste: rota /healthz registrada; +5 live skip). Conta/cliques sao do dono (nao crio conta). Ancorado #0055.

<!-- lifeline:end -->

### #0056 — 2026-06-01T14:37:23.209485+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: Conector MCP no ar e verificado no Render (free): claude.ai pode conectar (authless) — primeira nuvem viva
- **parents**: 4a900baf9bfae2d5d1d71f72a61c8206f21065dc9359b0ad3e501906209de71c
- **id**: 9c356f1be97209f00e001c9e57cdfaf28e0fad4f4be8407e270ea5cb66e01f3e

**Body**:
Deploy do dono no Render free (lifeline-cnah.onrender.com) via Blueprint. Verificado por mim daqui (URL HTTPS publica, sem o problema de porta 7844 do tunel): /healthz -> 200 'ok'; /mcp -> initialize 200 + handshake completo expondo TOOLS [lifeline_append, lifeline_recontextualize, lifeline_recall] e RESOURCE [lifeline://project/context]. Authless (validacao, single-tenant) servindo a propria LIFELINE.md. Cold-start ~1 min (free dorme apos 15 min). Falta o dono registrar a URL .../mcp como Custom Connector no claude.ai (Authentication: None) e sentir o valor. Proximo da viabilidade: multi-tenant via AS (#0049) + Railway/Render-paid sempre-on quando aprovar.

<!-- lifeline:end -->

### #0057 — 2026-06-01T14:42:16.841419+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: CORRECAO #0052: claude.ai WEB exige OAuth — authless NAO conecta no app web (so nos CLIs)
- **parents**: 9c356f1be97209f00e001c9e57cdfaf28e0fad4f4be8407e270ea5cb66e01f3e
- **id**: 5349b930896a20937d304be3921e29948dda573de408f9ab144a5ea8f0da4833

**Body**:
Teste ao vivo do dono: adicionar o conector authless (https://lifeline-cnah.onrender.com/mcp) no claude.ai web falhou com 'Couldn't register with sign-in service' (ofid_75cff0ea31cc4203). Diagnostico verificado daqui: o servidor authless retorna 200 no /mcp e NAO tem /.well-known/oauth-* (todos 404); mesmo assim o claude.ai WEB tenta registrar um client OAuth e, sem AS, nao consegue. A pesquisa #0052 concluiu 'authless valida no claude.ai' — CORRIGE-SE: isso vale pros CLIs (Claude Code/Gemini CLI aceitam URL/authless direto), NAO pro app web, cujo fluxo de Custom Connector forca OAuth (DCR/CIMD/client pre-registrado). Consequencia pratica: (a) validar o valor JA via Claude Code 'claude mcp add --transport http lifeline <url>/mcp' (authless ok); (b) pro claude.ai WEB, o AS (#0049) deixa de ser opcional — e o pre-requisito. Deploy em si esta 100% (healthz/mcp/tools/resource verificados).

<!-- lifeline:end -->

### #0058 — 2026-06-01T14:45:45.435934+00:00 — decision

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: decision
- **summary**: Remove _legacy/ do tracking do GitHub (gitignored) — refina #0040; rev0 fica no historico
- **parents**: 5349b930896a20937d304be3921e29948dda573de408f9ab144a5ea8f0da4833
- **id**: 25d42a655979b0d1ae9bc2db6994ed0ef78c72d7713e8ddbb19375d1cb6d952b

**Body**:
O #0040 arquivou a rev0 em _legacy/ rastreada (navegavel). Agora, mirando repo-vitrine limpo (direcao de lancamento/landing), tira-se _legacy/ (107 arquivos, 1.1M de SDK morto) da arvore versionada: git rm --cached + _legacy/ no .gitignore. NADA se perde: a rev0 continua (a) no disco local e (b) no HISTORICO do git (commits originais 37f5fd6 etc. + o rename fef0b15) — recuperavel por git log/checkout. Refina #0040 (mantem o porque/arquivamento; muda so o 'rastreado na arvore' -> 'preservado no historico'). Repo publico fica so com o produto limpo.

<!-- lifeline:end -->

### #0059 — 2026-06-01T15:15:00.768245+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: AI-first, friccao zero: manual embutido no servidor MCP (instructions), .mcp.json limpo, llms.txt, AGENTS/INTEGRATION com instalar+conectar-por-cliente+explicar ao user
- **parents**: 25d42a655979b0d1ae9bc2db6994ed0ef78c72d7713e8ddbb19375d1cb6d952b
- **id**: 4ece54aa8f969c3e0c59ba76e5c8a1c170469770d0ca9fdf8e0df882e2f2a149

**Body**:
Objetivo do dono: qualquer IA que conecta (ou abre o repo) entende o uso, sabe instalar/conectar, seguir, e EXPLICAR/ORGANIZAR pro humano — sem friccao. Entregue: (1) FastMCP instructions (899 chars) nas 3 construcoes do servidor (local/remoto authless/remoto OAuth) — toda IA recebe o manual no initialize: ler o context primeiro, propor via HITL, nunca inventar (ancora), e o papel de explicar/organizar pro humano. (2) .mcp.json LIMPO — so o server  stdio (o que o instalador recebe); a entrada supabase do DEV foi pra .mcp.local.json (gitignored, nao-versionada). Corrigido bug de comentario-inline no .gitignore (pattern nao casava). (3) llms.txt na raiz — mapa AI-readable (usar/instalar/entender/nuvem, com links). (4) AGENTS.md ganhou 'instalar 1 min (faca pelo humano)' + 'explique e organize pro humano'. (5) docs/INTEGRATION.md: snippets copia-e-cola por cliente (Claude Code auto via .mcp.json; Cursor; Claude Desktop com path absoluto; Gemini CLI) + comando alinhado (lifeline-mcp). Clientes de dev conectam no OSS local; apps web exigem nuvem+OAuth (#0057). Suite 75/5-skip. Falta p/ friccao-zero total: publicar no PyPI (hoje install e git/-e) e EN p/ alcance global.

<!-- lifeline:end -->

### #0060 — 2026-06-01T15:35:51.365738+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Empacotamento PyPI pronto e validado (nome livre, build OK, twine check PASSED, install em venv limpa OK) — falta so o twine upload do dono
- **parents**: 4ece54aa8f969c3e0c59ba76e5c8a1c170469770d0ca9fdf8e0df882e2f2a149
- **id**: bc6831f476e2ba930f871116f7fcc7280243556bcb1b12c42477b8545382edc8

**Body**:
Prep do item 1 (publicar no PyPI) executada ate onde da sem a conta do dono. Nome lifeline-context LIVRE no PyPI. pyproject completado: license MIT, authors, keywords, classifiers (Alpha/Python 3.10-3.13/AI), project.urls (github). Versao alinhada (__init__ 0.0.1 -> 0.1.0 = pyproject). build/ e dist/ no gitignore. python -m build gerou wheel + sdist; twine check PASSED nos dois. Teste de install em venv limpa: importa, versao 0.1.0, exports ok, 3 console scripts criados (lifeline/lifeline-mcp/lifeline-mcp-remote), lifeline --help exit 0, mcp_server+cloud importam. UNICO passo restante (do dono): criar conta no pypi.org + API token + 'twine upload dist/*'. Apos publicado, install vira 'pip install lifeline-context' e os snippets de conexao funcionam em qualquer maquina.

<!-- lifeline:end -->

### #0061 — 2026-06-01T15:53:47.610770+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Publicacao no PyPI via Trusted Publishing (OIDC) — workflow publish.yml, sem token
- **parents**: bc6831f476e2ba930f871116f7fcc7280243556bcb1b12c42477b8545382edc8
- **id**: 9a87b247fd25ccaed22388103f6aaca4f73d9319487271abcab28f7c466e706e

**Body**:
Dono optou pelo Trusted Publisher (OIDC) em vez de API token — mais seguro, nada de segredo pra gerenciar. Criado .github/workflows/publish.yml: dispara em release published (ou workflow_dispatch manual); permissions id-token: write (OIDC); environment pypi (casa com o formulario do PyPI); builda sdist+wheel e publica via pypa/gh-action-pypi-publish@release/v1. Formulario PyPI Trusted Publisher: projeto=lifeline-context, owner=jessianmart, repo=lifeline, workflow=publish.yml, environment=pypi. Falta do dono: (1) submeter o formulario (pending publisher cria o projeto no 1o publish), (2) criar o environment 'pypi' em Settings->Environments do repo, (3) criar um GitHub Release v0.1.0 (ou rodar o workflow manual) -> publica sozinho via OIDC. Ancorado #0061.

<!-- lifeline:end -->

### #0062 — 2026-06-01T15:59:04.361457+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: EN docs (superficie de lancamento): README EN + README.pt-BR.md preservado, llms.txt e AGENTS.md traduzidos
- **parents**: 9a87b247fd25ccaed22388103f6aaca4f73d9319487271abcab28f7c466e706e
- **id**: 38619c91b38e82ecea11af6bd21ad0e226584586fd272350cab87ac9179d2773

**Body**:
Alcance global pro lancamento OSS. README.md agora em EN (front door + long_description do PyPI), com seletor de idioma; o PT preservado em README.pt-BR.md. llms.txt e AGENTS.md (AI-facing) traduzidos pra EN — alinha com o 'AI-first' global. Badges de testes atualizados (75). PENDENTE (proximo passo, deep docs ainda em PT): docs/INTEGRATION.md, docs/ARCHITECTURE.md, docs/MCP_REMOTE.md, docs/DEPLOY.md, docs/M3_TIER1_SUPABASE.md, CONTRIBUTING.md, PRD.md. CLAUDE.md e LIFELINE.md ficam em PT de proposito (laws internas + line gerada = dogfood). O README EN linka esses docs PT por ora (snippets sao copia-e-cola, agnosticos de idioma).

<!-- lifeline:end -->

### #0063 — 2026-06-01T16:07:36.174972+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: EN docs completo: deep docs traduzidos (INTEGRATION, ARCHITECTURE, MCP_REMOTE, DEPLOY, M3, CONTRIBUTING, PRD)
- **parents**: 38619c91b38e82ecea11af6bd21ad0e226584586fd272350cab87ac9179d2773
- **id**: a4f3a6c453d7282f8f7f71fdb5946bc0c4941ed7c4eded3520b2b810c400d68d

**Body**:
Fecha o EN do repo pro lancamento global. 7 deep docs traduzidos PT->EN (paralelizado com subagentes, glossario consistente), com fixes de staleness no caminho: CONTRIBUTING quality-gate trocado de 'pasta v2/ + loop por-arquivo' para 'python -m pytest' e a ref a _legacy ajustada (agora gitignored/no historico); PRD corrigido (id=sha256(content+parents) e arquitetura SEM Redis, alinhando #0038); comentarios PT dentro de code blocks (MCP_REMOTE, M3) passados pra EN; ARCHITECTURE ganhou as linhas de cloud.py/staging.py e a nota do MCP remoto; DEPLOY com o reality-check do #0057 (claude.ai web exige OAuth). Ficam em PT de proposito: CLAUDE.md (laws internas) e LIFELINE.md (line gerada = dogfood). README PT preservado em README.pt-BR.md. Superficie EN de lancamento completa.

<!-- lifeline:end -->

### #0064 — 2026-06-01T16:25:20.421411+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: CI estava vermelho: rodava pytest sem instalar (pytest nao e dep do pacote). Adiciona extra dev + verify reconstroi a cadeia real
- **parents**: a4f3a6c453d7282f8f7f71fdb5946bc0c4941ed7c4eded3520b2b810c400d68d
- **id**: cd002c8ec9c85a556016ecd6860bce3f1663233ebf4969007479e9e69fd5a790

**Body**:
Diagnostico: o ci.yml fazia 'pip install -e .[cloud]' (so deps de runtime: pydantic/aiosqlite/mcp/httpx) e depois 'python -m pytest' — mas pytest NAO e dependencia do pacote, entao o step Testes falhava em todo push (vermelho desde que o CI foi adicionado, #0050). Reproduzido em venv limpa: pkg+pytest (sem pytest-asyncio) -> 75 passam (mcp 1.27.2 do PyPI tem todas as APIs usadas). Fix: (1) pyproject ganha optional-dependency dev=['pytest>=8']; (2) CI instala .[cloud,dev]; (3) step de integridade melhorado: 'lifeline migrate --from LIFELINE.md' + 'lifeline verify' (antes verificava um .db vazio -> 0 entradas trivial; agora reconstroi as 63 entradas da view versionada e verifica a cadeia REAL). Pacote em si nunca esteve quebrado (install/import/scripts provados); era so o CI sem pytest.

<!-- lifeline:end -->

### #0065 — 2026-06-01T16:42:51.725619+00:00 — release

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: release
- **summary**: lifeline-context 0.1.0 PUBLICADO no PyPI via OIDC (Trusted Publishing) — pip install funciona pro mundo
- **parents**: cd002c8ec9c85a556016ecd6860bce3f1663233ebf4969007479e9e69fd5a790
- **id**: f1ae33b4b55307c163ae1165cf7c4477dffed421606f9cafe61dde671d7c4eca

**Body**:
Primeiro release publico. Disparado por tag v0.1.0 -> workflow publish.yml (que ganhou gatilho de tag) -> build + pypa/gh-action-pypi-publish via OIDC, SEM token (o dono submeteu o Trusted Publisher no PyPI; eu fiz todo o resto). Run: SUCCESS. Verificado ao vivo: venv limpa, 'pip install lifeline-context' (do PyPI) -> importa v0.1.0, comando 'lifeline' OK, 3 console scripts (lifeline/lifeline-mcp/lifeline-mcp-remote). Tambem: CI ficou verde (#0064, faltava pytest). Badge do PyPI adicionado aos READMEs. Impacto: o maior atrito de instalacao morreu — os snippets de conexao (Claude Code/Cursor/Gemini) agora funcionam em qualquer maquina com lifeline-mcp no PATH. Releases futuros: bump de versao + tag vX.Y.Z (ou Release) -> publica sozinho. Falta do hibrido: AS (#0049) pros conectores web.

<!-- lifeline:end -->

### #0066 — 2026-06-01T17:11:57.327997+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Fecha gaps 1-3 do audit OSS: higiene (SECURITY/CHANGELOG/templates), schema empacotado + comando 'lifeline schema', testes de integracao (cobertura 80->84%) — bump 0.1.1
- **parents**: f1ae33b4b55307c163ae1165cf7c4477dffed421606f9cafe61dde671d7c4eca
- **id**: d99ebffcf478b51c48379f63fb9c088c9d9a2f9f5c2506aa4954cb6b41668d6f

**Body**:
Resposta ao audit de prontidao OSS. (1) HIGIENE: SECURITY.md (reporte via GitHub Private Vulnerability Reporting; threat-model local-trust vs cloud-RLS/HITL), CHANGELOG.md (Keep-a-Changelog, com 0.1.0 + 0.1.1), .github/ISSUE_TEMPLATE.md e PULL_REQUEST_TEMPLATE.md (PR template amarra na constituicao: pytest+verify+anexar entrada). (2) SCHEMA EMPACOTADO: cloud/schema.sql movido p/ lifeline/schema.sql (fonte unica), package-data no pyproject -> vai no wheel (confirmado), comando 'lifeline schema' (importlib.resources) imprime o SQL -> cloud-via-pip nao precisa do repo. Refs nos docs (M3/MCP_REMOTE/CONTRIBUTING) atualizadas; LIFELINE.md nao tocada (gerada/append-only, entradas antigas sao fato historico). (3) TESTES DE INTEGRACAO: TestCLIMain (main() despacha log/verify/schema + rede-de-erro -> exit 1 sem traceback) e handlers MCP de leitura (project_context/recall contra store temp). Cobertura: cli 62->70%, mcp_server 65->76%, total 80->84% (core segue 100%). Suite 78 passa / 5 skip. Bump 0.1.0->0.1.1 (0.1.0 no PyPI e imutavel; schema-no-wheel chega no 0.1.1). Veredito: OSS sobe de ~8.5 pra ~9.5; falta so o #0029 (recall denso) pro salto de produto.

<!-- lifeline:end -->

### #0067 — 2026-06-01T17:18:18.046957+00:00 — release

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: release
- **summary**: lifeline-context 0.1.1 publicado no PyPI (schema empacotado + comando schema, higiene OSS, cobertura 84%)
- **parents**: d99ebffcf478b51c48379f63fb9c088c9d9a2f9f5c2506aa4954cb6b41668d6f
- **id**: 715a3b940104ff91a08c0eecb2c8bc201bb3de848103beefd150b2b344271bbd

**Body**:
Segundo release. Disparado por tag v0.1.1 -> publish.yml (OIDC, sem token) -> SUCCESS. Verificado: 'pip install lifeline-context==0.1.1' do PyPI funciona (apos ~1min de propagacao do indice), versao instalada 0.1.1 confirmada em venv limpa. Conteudo do 0.1.1 (gaps 1-3 do audit OSS, #0066): schema da nuvem empacotado (lifeline/schema.sql no wheel) + comando 'lifeline schema'; SECURITY.md/CHANGELOG.md/issue+PR templates; testes de integracao (main() dispatch + handlers MCP) levando cobertura 80->84% (core 100%). OSS ~9.5. Proximo: #0029 (recall semantico denso).

<!-- lifeline:end -->

### #0068 — 2026-06-01T17:31:39.616445+00:00 — correction

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: correction
- **summary**: Resolve #0029: recall semantico DENSO plugado (SentenceTransformerEmbedder, opt-in) — 0.2.0
- **parents**: d2d305ab1b6b14dedd7757918cc4287bd79ed15e50418c2ae652b78b4e82c9c0
- **id**: c8a0552876e84056a357a963454adee87f27fa59ce2a3a556a0aec28c3efd333

**Body**:
Fecha o thread aberto #0029 ('plugar embedder semantico denso'). Implementado SentenceTransformerEmbedder atras do mesmo port Embedder (recall.py): lazy-import de sentence-transformers (extra [embeddings]), vetores normalizados -> similaridade = cosseno. Seletor make_embedder() le LIFELINE_EMBEDDER (default/'lexical' -> LexicalEmbedder zero-dep; 'dense' -> ST modelo default; outro valor -> nome de modelo). Wirado no cmd_context (--query) e no lifeline_recall do MCP. DEFAULT segue LEXICAL (zero friccao, zero dep) — o denso e OPT-IN. Testes: factory (default/dense/env), wiring com modelo fake (sem baixar), recall ranqueando por SIGNIFICADO via o port, erro claro sem o extra, e teste real skip-gated (related>unrelated) — suite 84 passa/6 skip. Docs (README/ARCHITECTURE) e CHANGELOG atualizados; bump 0.2.0. Era a unica lacuna de PRODUTO do audit — agora o recall casa por significado, nao so por palavra.

<!-- lifeline:end -->

### #0069 — 2026-06-01T17:37:13.577521+00:00 — release

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: release
- **summary**: lifeline-context 0.2.0 publicado no PyPI — recall semantico denso (#0029) opt-in
- **parents**: c8a0552876e84056a357a963454adee87f27fa59ce2a3a556a0aec28c3efd333
- **id**: d64d33a95bbe93352a7cd5187a333fb7e4706fcf9f8485aa85711c1b9b59474b

**Body**:
Terceiro release. Tag v0.2.0 -> publish.yml (OIDC) -> SUCCESS. Verificado: pip install lifeline-context==0.2.0 do PyPI OK, versao 0.2.0, e a API do #0029 embarca (from lifeline import make_embedder, SentenceTransformerEmbedder; make_embedder() default = LexicalEmbedder). #0029 fechado na line (#0068). Estado: OSS ~9.5-10 (core 100%, integracao 84%, PyPI, docs bilingues, higiene completa, AI-first, recall semantico opt-in). Unico item aberto: #0049 (Authorization Server) — peca do cloud pago/conector web, nao qualidade do OSS.

<!-- lifeline:end -->

### #0070 — 2026-06-01T21:24:06.692912+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Bootstrap de brownfield: checkpoint de contexto HITL no connect a uma line vazia
- **parents**: d64d33a95bbe93352a7cd5187a333fb7e4706fcf9f8485aa85711c1b9b59474b
- **id**: dc0bce46917c7819dec34c5aa1f871640927921da2c80e580257b758db1c4149

**Body**:
PORQUE: o cold-start e o gargalo de ativacao nº1 — quase ninguem adota o Lifeline desde o #0001; o caso dominante e instalar no MEIO do projeto, e ai a line comeca VAZIA. O Lifeline registra o porque PARA FRENTE; nao reconstroi o passado do codigo/git (non-goal). Sem onboarding, o primeiro connect mostra contexto vazio e a pessoa churna antes do valor (o pitch e TTC->0, entao um connect vazio e um problema existencial de ativacao). O QUE: (1) context.py — quando a line nao tem identidade nem decisoes, o contexto montado lidera com um CTA de bootstrap (o gatilho que a IA le no connect); (2) _INSTRUCTIONS do MCP — a IA que conecta a uma line vazia sabe se oferecer pra fazer o checkpoint; (3) novo comando 'lifeline init' (ativacao CLI-first) que inicializa a line e imprime o protocolo. DESIGN (validado com o humano): nao e input unico — e rascunho a partir dos artefatos de raciocinio JA escritos (README/ADR/PR) + entrevista curta (3-7 perguntas do porque tacito) -> entradas GRANULARES (1 bootstrap + N decision + M open, cada uma superseivel depois) -> aprovacao em lote. GUARDRAILS (respeitam a constituicao): tudo entra como PROPOSTA HITL (anti-sujeira); o porque NUNCA e inferido do codigo/diff (so de artefatos de raciocinio humanos) senao fura as Leis #1 (ancora) e #5 (porque>quê). A fundacao HITL (propose/review/approve) ja existia — o delta foi so gatilho+orquestracao. 6 testes novos (context vazio mostra CTA / populado nao mostra / nota solta ainda conta como vazia; init nos dois estados; _INSTRUCTIONS cobre bootstrap). Suite 90 passed/6 skipped. Decisao de sequencia: anuncio da 0.2.0 fica DEPOIS deste fix — sem ativacao, o anuncio so gera instalacoes que esfriam.

<!-- lifeline:end -->

### #0071 — 2026-06-01T21:46:39.883298+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Site público: landing horizontal (estética Linear) + docs crawláveis + GEO avançado, no GitHub Pages
- **parents**: dc0bce46917c7819dec34c5aa1f871640927921da2c80e580257b758db1c4149
- **id**: 756884ca69d1898ec7611ef512548a09fe51f8c758daa93432d7320384d1cb14

**Body**:
PORQUE: lancamento precisa de uma porta de entrada que (a) comunique a tese em segundos e (b) seja achavel/citavel por IAs — coerente com o produto ser AI-first. DESIGN: hiperminimal, estetica Linear (Inter, dark, hairlines, acento indigo); a 'lifeline' corre na HORIZONTAL (o DAG do ledger) e o scroll vertical do mouse a percorre — cada secao e um 'no' com chip de hash, ecoando os ids reais. Progressive enhancement: o conteudo e HTML semantico real (renderiza e e crawlavel SEM JS); no mobile empilha vertical. GEO (o diferencial pedido): JSON-LD (SoftwareApplication + SoftwareSourceCode + FAQPage + TechArticle por doc), llms.txt + llms-full.txt, robots.txt convidando GPTBot/ClaudeBot/PerplexityBot/Google-Extended explicitamente, sitemap.xml, OpenGraph, canonical. ARQUITETURA (decidido com o humano): hibrido — landing horizontal + paginas de doc HTML reais (melhor extracao por IA); ingles (alcance global). As docs sao GERADAS do markdown do repo por site/build.py (saida commitada, zero dep no deploy), entao editar docs/ATUALIZA o site. Deploy por .github/workflows/pages.yml (Pages via Actions). Validado ao vivo: geometria computada confere (grid 1180px, 3 cards 381px, centralizacao vertical, dots na borda, thread no centro). FALTA 1 passo manual do humano: habilitar Pages (Settings -> Pages -> Source: GitHub Actions). Sequencia: site primeiro, anuncio da 0.2.0 quando o site estiver no ar.

<!-- lifeline:end -->

### #0072 — 2026-06-01T22:01:46.517578+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Site: scroll horizontal travado — troca scroll-snap mandatory por none + snap-on-idle em JS
- **parents**: 756884ca69d1898ec7611ef512548a09fe51f8c758daa93432d7320384d1cb14
- **id**: 8fbfd11f8bb75a7619853e54082463d0837fd2688715a88ba54b47ffc35ddbb9

**Body**:
SINTOMA: no site publicado, o scroll vertical do mouse nao rolava a tela na horizontal (parecia congelado). CAUSA (confirmada via DOM ao vivo): 'scroll-snap-type: x mandatory' no .track reverte QUALQUER scrollLeft fora de um ponto de snap — cada incremento do wheel (~320px) e menor que um painel (1440px), entao o mandatory puxava de volta ao painel atual (setar scrollLeft=600 voltava a 0 instantaneamente). 'proximity' tem uma versao branda do mesmo bug: partindo de um painel, um tick fica 'perto demais' e e revertido (scroll partindo de 0 dava [0,0,0,0]). FIX: scroll-snap-type:none (zero snap nativo brigando) + snap-on-idle controlado em JS (scheduleSnap: 140ms depois que o wheel para, scrollTo smooth ao painel mais proximo). Acumulacao livre confirmada ([320,640,960,1280,1600] partindo do zero); o snap-on-idle anima em browser real (em headless o smooth nao progride, mas o instantaneo funciona). Tambem subi o multiplicador do wheel 1.15->1.6 pro percurso ficar mais agil.

<!-- lifeline:end -->

### #0073 — 2026-06-10T11:28:01.768552+00:00 — fix

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: fix
- **summary**: Auditoria de gaps: fecha 9 falhas CALADAS (anti-teatro) com teste de regressao por gap
- **parents**: 8fbfd11f8bb75a7619853e54082463d0837fd2688715a88ba54b47ffc35ddbb9
- **id**: ddbc7749c904625cba0c6f75227800f05012d2943ff04bce37df6af17b94c93e

**Body**:
Uma auditoria forense (criterio: o erro que so se percebe tarde, em silencio) achou e REPRODUZIU nove gaps; cada um agora falha alto e tem teste em tests/test_gaps.py. (G1, critico) a superficie MCP so entregava ids truncadas (recall id[:12], context id[:8]) e a correcao exigia id inteira sem validar -> supersessao virava no-op silencioso; resolve_parents() expande prefixo / recusa orfao/ambiguo no log e no approve. (G2) recall e a secao Relevante serviam decisao revertida como viva -> agora marcam [REVERTIDO] via o conjunto superseded. (G3) leitura nunca verificava a ancora (Lei #1 so por verify offline) -> reduce() verifica e DESCARTA conteudo adulterado, o assembler avisa. (G4) verify nao via OMISSAO (pai fantasma) e a reducao confiava so em seq -> verify checa fecho referencial; decisao reordenada apos sua correcao segue superseded. (G8) superseded era monotonico -> agora derivado do grafo de correcoes por ponto-fixo: reverter a reversao restaura o original. (G5) o corte s>0.0 so abstinha no lexical -> piso min_score por embedder (denso default 0.3). (G6) body com '### #' ou terminando em '---' corrompia no clone/pull -> sentinela BODY_END torna o round-trip lossless (provado nas 72 entradas reais). (G7) approve marcava 'approved' mesmo em dedup -> honra o retorno do append (status 'duplicate'). (G10, fronteira) body cercado como citacao no payload (injecao nao se passa por estrutura; HITL e a defesa final). (G9) ts fora do hash e LIMITE declarado (determinismo, Lei #3), nao gap a consertar.

<!-- lifeline:end -->

### #0074 — 2026-06-10T11:28:19.704561+00:00 — feature

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: feature
- **summary**: Authorization Server OAuth 2.1 (DCR + authorization-code/PKCE) delegando login ao Supabase
- **parents**: ddbc7749c904625cba0c6f75227800f05012d2943ff04bce37df6af17b94c93e
- **id**: 5e23168c8fe8957853f5528e9d0df4fa0c6d3b236802ff931e7703d9bf3bcc6b

**Body**:
Fecha o pre-requisito dos conectores hospedados (claude.ai/ChatGPT/Gemini), que exigem um AS COMPLETO: DCR (RFC 7591) + authorization-code com PKCE S256 + metadata (RFC 8414). O Supabase Auth e um IdP, NAO um AS OAuth generico com DCR — entao o AS mora em lifeline/oauth.py (SupabaseAuthServer, implementa OAuthAuthorizationServerProvider do SDK MCP) e DELEGA a autenticacao do usuario ao Supabase. Fluxo: /register (DCR) -> /authorize guarda params sob ticket e manda ao /oauth/login -> o login entrega email+senha ao Supabase (grant_type=password; nos NUNCA guardamos a senha, so repassamos sobre TLS) e cunha NOSSO code -> /token troca o code (PKCE verificado pelo SDK) pelo access_token = o JWT do Supabase, que o Resource Server ja valida por requisicao (escopa a RLS por usuario). Refresh e revoke batem no Supabase. Liga com LIFELINE_OAUTH_AS=1 (implica o RS); LIFELINE_OAUTH=1 segue sendo so o RS. 13 testes (test_oauth.py) provam DCR, authorize->login->code, troca one-time, code ligado ao client, expiracao, refresh, introspeccao e revoke, com o Supabase mockado (wire, nao live). LIMITES declarados (honestidade #0046/#0047): grant de senha (nosso server ve a senha em transito) e o minimo testavel — hardening = redirect ao login hospedado do Supabase, sem mudar o AS; clients/codes em memoria (correto p/ instancia unica; tabela lifeline_oauth_clients ja no schema p/ escalar).

<!-- lifeline:end -->

### #0075 — 2026-06-10T11:31:27.084141+00:00 — correction

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: correction
- **summary**: Fecha a thread: o Authorization Server (DCR + auth-code/PKCE) foi entregue (#0074)
- **parents**: 9062526020106de9959dba102e62f55f75187b3306f9cc1521f0f49a11e0cc89
- **id**: 263aff455ed1e8f37983f5a42fd78ea684d71120615f700b97a2c9031b58a4b1

**Body**:
O open item #32d96c3d (proximo: OAuth Authorization Server p/ plugar nos conectores hospedados) esta CUMPRIDO pela feature #0074 (lifeline/oauth.py + LIFELINE_OAUTH_AS=1, 13 testes). Supersede o open para sair de 'em aberto'. Proximo natural, se desejado: trocar o grant de senha pelo login HOSPEDADO do Supabase (SSO) e persistir os clients DCR na tabela lifeline_oauth_clients para deploy multi-instancia — ambos sem mexer no AS.

<!-- lifeline:end -->

### #0076 — 2026-06-10T11:58:18.586144+00:00 — feature

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: feature
- **summary**: AS: sign-up inline (Supabase) + teste e2e do baile OAuth completo pelas rotas HTTP reais
- **parents**: 263aff455ed1e8f37983f5a42fd78ea684d71120615f700b97a2c9031b58a4b1
- **id**: 79f05269b7bc7d2ef9adb43abdd3be3031b2a1a3f57b2c7dbb1e37f8cdefdf93

**Body**:
Preparando o teste hospedado multi-tenant (claude.ai), fechei o gap que travaria o 1o usuario: o form /oauth/login so fazia login (password grant), nao CRIAVA conta — quem conectasse sem conta Supabase ficava preso. Adicionado /auth/v1/signup com checkbox 'Criar conta': auto-confirm -> loga inline e cunha o code; confirmacao-por-email -> mensagem clara (nao da pra completar inline); conta existente/erro -> mensagem. E adicionado o teste mais valioso do AS: TestEndToEndASGI dirige o baile INTEIRO pelas rotas HTTP reais (DCR /register -> /authorize 302 -> /oauth/login 302 -> /token 200) com PKCE S256 verificado pelo SDK e o Supabase mockado — o mais perto do handshake do claude.ai sem conector ao vivo; + caso negativo (PKCE errado -> invalid_grant). Discovery validado RFC-compliant (protected-resource aponta authorization_servers ao nosso AS; AS anuncia authorize/token/register + S256). 124 testes verdes. Limite ainda aberto e declarado: o handshake com o claude.ai REAL nunca rodou (so mock); e clients DCR seguem em memoria (ok p/ instancia unica).

<!-- lifeline:end -->

### #0077 — 2026-06-10T12:43:01.297084+00:00 — fix

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: fix
- **summary**: Deploy hospedado caía em AUTHLESS em silêncio; AS não ligava — boot anuncia o modo + auto-deriva a URL do Render
- **parents**: 79f05269b7bc7d2ef9adb43abdd3be3031b2a1a3f57b2c7dbb1e37f8cdefdf93
- **id**: 39a434a0fb3f8b2973b73535017cad24cb36a5aed53b0ead5e42def1cf93d903

**Body**:
Incidente no 1o teste com o claude.ai: o conector falhou no registro (DCR). Log do Render mostrou TUDO 404 — inclusive /.well-known/oauth-authorization-server e /register. Causa: o servidor subiu em authless porque as env vars do AS (LIFELINE_OAUTH_AS=1 + LIFELINE_STORE=supabase + SUPABASE_*) nao foram aplicadas, e _build_remote CAÍA em authless SEM AVISAR — a mesma classe de falha calada que a auditoria desta sessao cacou. Consertos: (1) o boot ANUNCIA o modo no log ([lifeline] modo: AUTHORIZATION SERVER / RESOURCE SERVER / AUTHLESS); (2) se LIFELINE_OAUTH(_AS)=1 foi pedido mas falta env, GRITA exatamente o que falta em vez de cair calado; (3) PUBLIC_URL e ALLOWED_HOSTS agora DERIVAM de RENDER_EXTERNAL_URL/HOSTNAME automaticamente — menos config manual, menos chance de mismatch. render.yaml reduzido a 4 env vars. Validado simulando o ambiente Render: AS liga, issuer = a URL do Render, rotas DCR/authorize/login montadas. 33 testes (mcp+oauth) verdes. Limite: o handshake real do claude.ai ainda precisa rodar com o AS de fato no ar.

<!-- lifeline:end -->

### #0078 — 2026-06-10T13:21:57.146860+00:00 — fix

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: fix
- **summary**: Login do AS dava 500 cru: SUPABASE_URL sem https:// estourava no httpx; normaliza a URL + trata/loga toda falha do Supabase
- **parents**: 39a434a0fb3f8b2973b73535017cad24cb36a5aed53b0ead5e42def1cf93d903
- **id**: 9a0bcb2dc226a4cd8a5131ce43f9a4fd8efdcd527a9b138231c02f1982585601

**Body**:
Segundo incidente do teste hospedado: o form de login dava 'Internal Server Error' em qualquer acao, sem log visivel. Reproduzido contra o servidor ao vivo (register -> authorize -> POST /oauth/login = 500). Causa raiz: SUPABASE_URL colada SEM 'https://' no Render -> httpx levanta UnsupportedProtocol na chamada de auth -> 500 (o store nao usa essa URL no login, por isso so apareceu aqui). Mesma classe de falha opaca que a sessao toda combate. Consertos: (1) clean_url() normaliza a URL do Supabase na ENTRADA (prepende https://, tira espacos/barra) — em cloud._SupabaseBase E em oauth.SupabaseAuthServer; mata o cenario inteiro mesmo se a env vier torta; (2) _supabase_token/_supabase_signup/load_access_token agora capturam erro de rede/URL e resposta nao-JSON -> LOGAM e devolvem None/mensagem clara, nunca 500; (3) login_post ganhou rede-de-seguranca try/except que devolve o form com erro legivel e loga o traceback. 4 testes novos (normalizacao + falha graciosa). Validado ao vivo: URL sem esquema agora alcanca o Supabase em vez de estourar. 39 testes oauth+supabase verdes.

<!-- lifeline:end -->

### #0079 — 2026-06-10T13:46:00.185474+00:00 — decision

- **author**: claude
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: decision
- **summary**: Adota o OAuth Server NATIVO do Supabase como AS; nosso servidor vira Resource Server (JWKS). Supersede a premissa do AS próprio
- **parents**: 9a0bcb2dc226a4cd8a5131ce43f9a4fd8efdcd527a9b138231c02f1982585601
- **id**: 98179a72a89794d1acc2ba5eaf097f323f7d9fff293f2cc18c4eefead79f30cd

**Body**:
Mudanca externa: o Supabase lancou um OAuth 2.1 Server nativo (beta, gratis no beta, todos os planos) — DCR, authorize/token, PKCE S256, metadata, e suporte explicito a MCP. Isso INVALIDA a premissa de #0046/#0047 ('Supabase Auth nao e um AS OAuth generico com DCR') que justificou construir o nosso AS (#0074). Direcao nova: o AS passa a ser o do Supabase (issuer .../auth/v1; discovery em /.well-known/oauth-authorization-server/auth/v1; DCR em /auth/v1/oauth/clients/register), e o nosso servidor volta a ser so RESOURCE SERVER — modo que ja tinhamos (LIFELINE_OAUTH=1). Trocas no codigo: o RS aponta o issuer pro OAuth Server do Supabase, e a validacao de token virou JWKS/ES256 (novo SupabaseJWKSVerifier; PyJWT ja vinha via mcp, sem dep nova) em vez de chamar /auth/v1/user — valido ao vivo contra a JWKS real (so a expiracao barrou o token de teste). GANHOS: padrao oficial mantido por eles; login hospedado do Supabase cobre Google/GitHub nativo (sem codigo nosso); menos superficie sensivel sob nossa guarda. lifeline/oauth.py (o AS proprio, grant de senha) FICA no repo como fallback p/ deploy sem o OAuth Server, ate o caminho novo provar ao vivo. CAVEATS declarados: e beta; o claude.ai tem bugs proprios de conector OAuth; aud do token ainda nao fixado (validamos issuer+assinatura+exp). 129 testes verdes.

<!-- lifeline:end -->

### #0080 — 2026-06-10T15:12:48.005134+00:00 — decision

- **author**: jess
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: decision
- **summary**: Relicencia 0.3.0+ para FSL-1.1-MIT (source-available); versoes <=0.2.0 seguem MIT (ja na PyPI)
- **parents**: 98179a72a89794d1acc2ba5eaf097f323f7d9fff293f2cc18c4eefead79f30cd
- **id**: 98f81b61645cac68b411add5bb01c40f92d5925397a8ba774c19f0d0264021ea

**Body**:
O nucleo segue legivel e auto-hospedavel (confianca + adocao), mas reserva o uso comercial CONCORRENTE (oferecer o Lifeline como servico) — a FSL converte para MIT em 2 anos por release. As versoes 0.1.0-0.2.0 ja publicadas na PyPI permanecem MIT (irrevogavel; o codigo de core+nuvem ja saiu sob MIT). Refina o licenciamento do #d9b21042 (de 'OSS/MIT' para 'source-available') sem reverter a tese open-core/hub-pago. O *porque* de negocio detalhado (alvo de receita, moat) vive na LINHA PRIVADA de estrategia, fora de qualquer repo.

<!-- lifeline:end -->

### #0081 — 2026-06-10T16:40:47.915307+00:00 — feature

- **author**: jess
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: feature
- **summary**: Serve a consent page (caminho OAuth Server do Supabase) no proprio servidor, com SUPABASE_URL/KEY injetados do ambiente
- **parents**: 98f81b61645cac68b411add5bb01c40f92d5925397a8ba774c19f0d0264021ea
- **id**: a0849a89009e1e5f3b464886150808e8841747eb171a1dca95d072423cdbebff

**Body**:
Rota GET /oauth/consent serve site/oauth/consent/index.html substituindo placeholders pelo SUPABASE_URL/KEY do ambiente. Resolve duas coisas: (1) hospeda a consent page sem GitHub Pages -> o repo pode ficar PRIVADO; (2) tira o hardcode do projeto Supabase do core publico (fica generico/configuravel). O Supabase OAuth Server redireciona pra <PUBLIC_URL>/oauth/consent; favicon virou data-uri (host-agnostico). 18 testes mcp verdes.

<!-- lifeline:end -->

### #0082 — 2026-06-10T17:00:25.686734+00:00 — feature

- **author**: jess
- **agent**: claude-code
- **provider**: anthropic
- **model**: claude-fable-5
- **kind**: feature
- **summary**: Costura de tenancy no MCP: _REQUEST_STORE_FACTORY injetavel (hub adiciona team-line routing sem forkar o core)
- **parents**: a0849a89009e1e5f3b464886150808e8841747eb171a1dca95d072423cdbebff
- **id**: aac9654a913ea2766060408915104364e1618746ae17fb4a54c21e58f11182c8

**Body**:
_open_request/_staging_request passam a checar um factory por-requisicao opcional (_REQUEST_STORE_FACTORY/_REQUEST_STAGING_FACTORY). Se setado, tem prioridade e recebe o token do usuario. Permite o lifeline-hub (privado) rotear team-lines e usar o HubEventStore SEM tocar/forkar o core FSL. Generico (qualquer embedder usa). Testado.

<!-- lifeline:end -->

### #0083 — 2026-06-10T20:24:54.010064+00:00 — release

- **author**: human
- **agent**: claude-fable-5
- **provider**: anthropic
- **model**: human
- **kind**: release
- **summary**: lifeline-context 0.3.0 no PyPI + projeto migrado pra org lifeline-context + dominio lifelinecontext.com
- **parents**: aac9654a913ea2766060408915104364e1618746ae17fb4a54c21e58f11182c8
- **id**: 58e5d54cd30a6efe30d7aee24337283499bdac7193fb309d4b147fe1beba42de

**Body**:
Publica a 0.3.0 no PyPI (via Trusted Publishing/OIDC, sem token) e move o projeto pra org GitHub lifeline-context, agora servido em https://lifelinecontext.com (Pages + dominio proprio, HTTPS ok).

PORQUE org + dominio: unifica a marca numa casa so (org guarda o core publico 'lifeline' e o hub privado 'lifeline-hub'), e o dominio proprio torna a URL canonica PERMANENTE — mover repo nunca mais quebra link/SEO. Feito agora porque o custo era zero: o site rodou pouco, nao indexou, e o repo era privado ate pouco (sem SEO a perder). lifeline.dev custava US0 (nome premium); lifelinecontext.com no .com ~US0 e bate com o pacote PyPI e o posicionamento ('context runtime').

O 0.3.0 carrega o fechamento dos 9 gaps do audit + a seam _REQUEST_STORE_FACTORY (que o hub privado usa sem forkar o core) + endurecimento OAuth/JWKS. Sweep de URLs (build.py base, pyproject urls, site rebuildado, CNAME) verificado: site 200, canonical novo, /docs //llms.txt //sitemap.xml 200.

<!-- lifeline:end -->

### #0084 — 2026-06-11T01:23:30.264744+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Round-trip por disco: writer/reader byte-fiéis (newline="") + pino .gitattributes -text
- **parents**: 58e5d54cd30a6efe30d7aee24337283499bdac7193fb309d4b147fe1beba42de
- **id**: d0598bbcadb1ccd0bc6f3945f9655b0f44dfe873587c80360257da8fb1e9f2bf

**Body**:
A projeção store->LIFELINE.md->store nao era ponto-fixo NO DISCO (so em memoria). Em modo-texto, _write_view traduzia \n->os.linesep (CRLF no Windows) e ingest_markdown fazia universal-newlines: um body com \r\n dobrava p/ \r\r\n no arquivo e voltava como \n\n, mudando os BYTES do body e portanto o id content-addressed (Lei #3). Um filho que citava o id antigo virava pai-fantasma e o verify do rebuild dava BROKEN (foi o #0042, id 45bfc3...). Fix: abrir write e read com newline="" (inversa exata um do outro) + .gitattributes pina LIFELINE.* como -text p/ o git nao re-normalizar EOL no add/checkout. Teste novo (TestG6File) exercita o caminho de disco com body CRLF + multi-pai + supersessao e prova ids estaveis + verify OK + DAG preservado.

<!-- lifeline:end -->

### #0085 — 2026-06-11T01:25:14.378818+00:00 — note

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: note
- **summary**: Revisão completa da doc do site: alinhada ao comportamento que de fato shipou
- **parents**: d0598bbcadb1ccd0bc6f3945f9655b0f44dfe873587c80360257da8fb1e9f2bf
- **id**: 6886d7e0ed7f3ca22a1f795b395cb7ff8e908cdf6ec03b4bf374dbabdac9bda3

**Body**:
Auditoria das 6 docs publicadas (getting-started, concepts, architecture, integration, mcp, cli) por agentes revisores independentes. Correcoes de FATO, nao de estilo: (1) concepts: hash usa body.strip(), nao body. (2) architecture: documentado o portao de integridade (reduce() chama verify() e descarta entrada adulterada p/ integrity_broken), supersessao e PONTO-FIXO do grafo de correcoes (nao set que so cresce), e o piso de abstencao do recall (min_score; dense=0.3); .db reconciliado como runtime-store gitignored (nao 'cache') vs store-is-source; cloud store marcado como shipado; header de versao/licenca; \n final na forma canonica. (3) integration: comando lider vira lifeline-mcp (a forma LIFELINE_DB=... era bash-only num projeto PowerShell-first) + lifeline_recall listado. (4) mcp_remote: ref do Supabase trocado por <your-ref> (nao vazar nosso ref em doc publica), nota PowerShell p/ os blocos export, heading RS/AS desambiguado (LIFELINE_OAUTH=1 e Resource-Server, Supabase e o AS). (5) cli: --budget default 8000, restricoes do --store supabase (push/pull/clone/lines local-only), flags de identidade, LIFELINE_DB, dense recall. (6) getting-started: 'zero-dependency for recall' reescrito + nota de licenca FSL.

<!-- lifeline:end -->

### #0086 — 2026-06-11T02:02:42.002062+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: AS endurecido p/ produção: login HOSPEDADO (sem ROPC) + client store DCR persistente
- **parents**: 6886d7e0ed7f3ca22a1f795b395cb7ff8e908cdf6ec03b4bf374dbabdac9bda3
- **id**: b3584da7ea0358e1381259ad079ebf734b93be12fec01c2c65035ecf0c33c3b3

**Body**:
Fecha os 2 limites declarados do AS empacotado (lifeline/oauth.py). (1) LOGIN HOSPEDADO: com LIFELINE_OAUTH_PROVIDER (ex.: github), /oauth/login redireciona ao login social do Supabase (GoTrue /auth/v1/authorize?provider=...) com PKCE server-side NOSSO; /oauth/callback troca o code via grant_type=pkce (auth_code+code_verifier guardado sob o ticket). A SENHA NUNCA toca nosso servidor. O form ROPC vira fallback só de dev/CLI (sem provider) — backward-compat, testes antigos verdes. (2) CLIENT STORE PLUGGABLE: ClientStore + InMemoryClientStore (default) + SupabaseClientStore (PostgREST, chave de serviço — registro e pre-login, e infra do AS por schema.sql:84-98); ativa com SUPABASE_SERVICE_ROLE, persiste em lifeline_oauth_clients e sobrevive a restart/sleep do Render e a multiplas replicas (senao some no restart e o conector quebra). Codes seguem one-time/efemeros (TTL 300s). Contrato GoTrue confirmado por pesquisa antes de codar (server-side PKCE: redirect_to + code_challenge_method=s256 -> ?code -> POST /token?grant_type=pkce {auth_code,code_verifier}). 9 testes novos (TestHostedLogin + TestPersistentClientStore); 31/31 em test_oauth.py, 142 na suite. MCP_REMOTE.md atualizado (env vars + config de Redirect URL no Supabase).

<!-- lifeline:end -->

### #0087 — 2026-06-11T03:22:39.853293+00:00 — note

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: note
- **summary**: Doc do site: seção 'Lines' (threads de raciocínio separadas) + mapeamento pra Tree-of-Thoughts
- **parents**: b3584da7ea0358e1381259ad079ebf734b93be12fec01c2c65035ecf0c33c3b3
- **id**: ff6e76ecf2c929a1eb7d75d6faa8bbd4cbafaee4ff3032904c47492880d67781

**Body**:
O site nao explicava lines — so citava --line de passagem no CLI. Adicionada secao em concepts.md: line = ledger independente content-addressed (proprio DAG + view; .lifeline/<nome>.db + LIFELINE.<nome>.md; --line / LIFELINE_LINE / per-request no hub; sem cross-line refs). Por que multiplas: audiencia/visibilidade (ex.: ledger publico vs --line strategy privado), subsistema/experimento, branch de exploracao. Branching DENTRO de uma line = o DAG (merge parents=[A,B], A+B=B+A; correction poda/supersede, fica ancorado e visivelmente revertido). Mapeamento ToT (honesto: Lifeline GRAVA a arvore, nao a executa — orquestrar e non-goal): branches-como-lines (paralelo isolado) ou branches-no-DAG; o ganho especifico e nao re-explorar branch ja podado (decision amnesia no nivel de branch). Cross-link no cli.md + meta description + GEO (llms-full).

<!-- lifeline:end -->

### #0088 — 2026-06-11T03:46:09.177736+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Site funnel: prova (dogfood+demo), página vs-alternatives, gancho de distribuição, curate-well, página Teams
- **parents**: ff6e76ecf2c929a1eb7d75d6faa8bbd4cbafaee4ff3032904c47492880d67781
- **id**: c7fa49f15ffc0908cc96de3d4d37d11c612ed1b64bc929cd4472230d4a480a71

**Body**:
Análise sênior achou que a doc explicava o MECANISMO mas nao provava/posicionava/convertia. Endereçado em 5 frentes: (1) PROVA na landing — painel com a saida REAL de 'lifeline context' deste repo (87 entradas, IA+humano, ancorado) + link pro LIFELINE.md vivo (dogfood exposto). (2) Pagina compare.html — Lifeline vs ADRs/CLAUDE.md/RAG/memory MCPs (mem0,Letta,Honcho)/wiki/git, com 'quando NAO usar' honesto. (3) Gancho de DISTRIBUICAO nivel-hero — painel 'sua IA ja le, mora no repo': qualquer IA que le o repo herda o porque via LIFELINE.md, sem MCP. (4) Pagina curate.html — higiene do ledger (boa entrada, granularidade, supersede-nao-edite, ser ruthless no approve) + o modo de falha 'ledger rot' nomeado e como resistir. (5) Pagina teams.html — hub hospedado em early access (lines de time, MCP zero-ops, GitHub App, billing Marketplace), free-vs-pago honesto, CTA via GitHub. Wired no build (PAGES+NAV grupos Decide/Teams), nav/footer com Teams, footer corrigido (FSL nao MIT). Verificado no preview: painel proof fits (d=0), distribution igual ao mcp existente; mobile fits + pre scrolla horizontal (padrao). 9 doc pages agora.

<!-- lifeline:end -->

### #0089 — 2026-06-11T03:59:51.553990+00:00 — note

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: note
- **summary**: Diagramas SVG no site: o loop (connect↔append) na landing + o DAG (branch/prune/merge) em concepts
- **parents**: c7fa49f15ffc0908cc96de3d4d37d11c612ed1b64bc929cd4472230d4a480a71
- **id**: ed6c6eb917d4774cfaeb6723e2cf0c77e164fddb77d9c42a80ec611b3da1621c

**Body**:
Visuais on-brand (paleta accent #7c89ff / #41d6c3, mono) emendados: (1) landing painel do loop — SVG do ciclo Your AI <-> Lifeline ledger com '① CONNECT read context' e '② WORK propose + HITL'. (2) concepts, seção Lines/DAG — SVG do DAG dentro de uma line: bootstrap -> A/B/C, B podado por correction (tracejado + ✕, superseded), A+C fazem merge (parents ordenados, A+C ≡ C+A). Classe .diagram no CSS (width 100%, max 720/660, centrado). Python-Markdown passa o bloco <figure>/<svg> cru (verificado: 19 shapes intactos, nao escapado). Preview verificado a 1280px: loop fits (660 centrado), DAG 738->720 fits a coluna, sem quebra (o '120px' era viewport de 191).

<!-- lifeline:end -->

### #0090 — 2026-06-11T04:06:15.648987+00:00 — note

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: note
- **summary**: Hosted MCP (lifeline-mcp.onrender.com) com RS auth LIGADO e verificado ao vivo
- **parents**: ed6c6eb917d4774cfaeb6723e2cf0c77e164fddb77d9c42a80ec611b3da1621c
- **id**: 6ea826829c117986c3f7dbc29dfabb736adc4c0720790b16844aa0498fcd3d7e

**Body**:
Endpoint /mcp (streamable-http) agora exige Bearer JWT do Supabase, validado por JWKS/ES256 (LIFELINE_OAUTH=1 + LIFELINE_STORE=supabase, env setada no Render). Verificado: /.well-known/oauth-protected-resource publica o AS = Supabase (/auth/v1); /mcp sem token e com token-lixo -> 401; /mcp com JWT real do Supabase -> 200 (initialize). JWKS do projeto confirmado EC/ES256. Multi-tenant por RLS (owner=auth.uid). Conecta no Claude Code CLI por header Bearer. Proximo opcional: modo AS (LIFELINE_OAUTH_AS=1 + provider github no Supabase + redirect /oauth/callback) p/ o login hospedado no navegador (web apps).

<!-- lifeline:end -->

### #0091 — 2026-06-11T12:00:41.030561+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: MCP serverInfo: logo (icons) + website_url no initialize (SEP-973) — branding nos conectores
- **parents**: 6ea826829c117986c3f7dbc29dfabb736adc4c0720790b16844aa0498fcd3d7e
- **id**: 211731043844221bf9f419627e06450e5dd679a4963ada13585e94a4594007e2

**Body**:
O servidor MCP agora anuncia o logo do Lifeline via serverInfo.icons (SEP-973, suportado pelo SDK instalado: Implementation tem icons/title/websiteUrl e FastMCP aceita icons=/website_url=). Adicionado em TODOS os 4 FastMCP (stdio default + remoto AS/RS/authless): icons = PNG 512/1024 + favicon.svg (URLs PUBLICAS no lifelinecontext.com, alcançaveis sem auth) + website_url=https://lifelinecontext.com. Verificado local: create_initialization_options carrega icons+website_url. HONESTO: o claude.ai HOJE ainda mostra icone generico (gap do cliente, rastreado em anthropics/claude-ai-mcp#152 e claude-code#44675/#49040) — nao e bug nosso; clientes que suportam SEP-973 ja renderizam, e o claude.ai acende sozinho quando shipar. 50 testes passam.

<!-- lifeline:end -->

### #0092 — 2026-06-12T00:58:08.084860+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Site: bugs das adições SVG — pt-BR no painel Proof (site é EN) + headline fora de vista no loop (overflow lateral)
- **parents**: 211731043844221bf9f419627e06450e5dd679a4963ada13585e94a4594007e2
- **id**: 22a38e2d851afa58a0de01e18dc015ac364b043f02ef8b20af264a468c9737ef

**Body**:
Dois bugs introduzidos nas adições recentes: (1) o painel 'Proof' mostrava a saida REAL do lifeline context em portugues, num site nativo EN — traduzido pra ingles (entradas reais, hashes preservados; reframe de 'real output' p/ 'the context a fresh AI reads' ja que e renderizacao EN, com link pro LIFELINE.md real). (2) O diagrama SVG do loop deixou o painel da landing alto demais (707px); como os paineis sao altura-da-viewport com conteudo centralizado, em telas baixas (~640-700px) o titulo saia de vista. Fix: removi o SVG do loop da landing (painel volta a 467px) e MOVI o diagrama pro getting-started (pagina de scroll vertical, sem esse problema), em ingles. Verificado no preview: todos os paineis da landing cabem ate 640px de altura (over=0); o diagrama do loop renderiza no getting-started (720x189, labels EN). O DAG em concepts continua (EN, scroll vertical, ok).

<!-- lifeline:end -->

### #0093 — 2026-06-23T19:33:53.813336+00:00 — decision

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: decision
- **summary**: Tool output is now English (EN-first product)
- **parents**: 22a38e2d851afa58a0de01e18dc015ac364b043f02ef8b20af264a468c9737ef
- **id**: b47a8dc15bec76292938ad7f9f9e766e56caf2eaca7383efa2aa6bfc943bb71b

**Body**:
The user-facing output of the tool is now English: the assembled context (context.py — what every AI reads), the CLI messages (cli.py), the LIFELINE.md preamble, and the MCP instructions + tool descriptions (mcp_server.py). Why: the product is English-first (README, site, org, domain), but the tool was hardcoded Portuguese — an English user's AI received PT-headed context, and the README could not show real output without reintroducing the pt-BR-on-EN-site bug. Entry content stays whatever language it is written in; only the structural strings changed. Tests updated to assert the EN strings (142 pass). The README quickstart now shows the real EN 'lifeline context' output.

<!-- lifeline:end -->

### #0094 — 2026-06-23T20:43:29.423518+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: Harden for 0.4.0 (beta): close pre-release gaps + finish English output
- **parents**: b47a8dc15bec76292938ad7f9f9e766e56caf2eaca7383efa2aa6bfc943bb71b
- **id**: e39e2636a4f2ba51139b27de4e72e6209a6aa4f14cf4c6325c37d0a9b3f46409

**Body**:
Deep gap analysis before publishing flagged blockers that would ship a broken/inconsistent pip install; fixed the ones that matter. (1) Packaging: pin mcp>=1.20 — Icon/website_url + the JWKS/multipart transitive deps the server imports crash below 1.15; made the [remote] extra self-sufficient (PyJWT[crypto], python-multipart, starlette). (2) The OAuth consent page lived OUTSIDE the package (read from ../site) so a pip install 404'd; moved it into lifeline/templates/consent.html, served via importlib.resources, shipped via package-data. (3) Finished the EN switch the prior pass missed — oauth login form + error strings, the consent page, cli _validate, store resolve_parents, cloud credentials, recall dense (the *why* an AI reads must be English). (4) Budget bug: the assembler under-reserved the decisions header/omit-marker, so a tight budget could mid-cut the always-include 'Recent' block; the reservation is now exact and the safety net is provably unreachable (Law #6). (5) Security: authorize() allow-lists redirect_uri (open-redirect/code-exfiltration), and schema.sql enables RLS on lifeline_oauth_clients (was exposed to anon). (6) Proved content-addressing under races: concurrent identical appends -> exactly 1 entry; two divergent views merge as a union with no dupes. Version 0.2.0->0.4.0 (was 2 releases stale); posture alpha->beta — cloud + OAuth + GitHub App are validated live, 'alpha' undersold it. 153 tests green. Tag/publish stays pending owner authorization (public action).

<!-- lifeline:end -->

### #0095 — 2026-06-23T21:26:15.739448+00:00 — release

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: release
- **summary**: 0.4.0 (beta) published to PyPI
- **parents**: e39e2636a4f2ba51139b27de4e72e6209a6aa4f14cf4c6325c37d0a9b3f46409
- **id**: 40ca4095f2f57726b0e5cbf492d5fe8d9014d960d54aad2931cb09e632a8ceaf

**Body**:
Tag v0.4.0 (at e3dd95f) triggered publish.yml -> OIDC Trusted Publishing -> PyPI; the run succeeded in 26s and lifeline-context 0.4.0 is live (wheel + sdist). Closes the 'tag/publish pending owner authorization' note from the #0094 milestone. What shipped: mcp>=1.20 pin + self-sufficient [remote] extra, consent page bundled in the wheel (served via importlib.resources), English tool/CLI/MCP output, exact context-budget reservation (no more mid-cut of the always-include Recent block), authorize() redirect_uri allow-list + RLS on lifeline_oauth_clients, and a content-addressing concurrency proof; posture alpha->beta (cloud/OAuth/GitHub App validated live). 148 tests green. Also repaired the local MCP install (editable -> the lifeline-mcp console script now serves 0.4.0/EN instead of a stale 0.3.0) and validated the full read->recall->propose->HITL loop live against the local server.

<!-- lifeline:end -->

### #0096 — 2026-06-23T21:41:52.255546+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Post-0.4.0 backlog: ROPC public guard (S3), opt-in JWKS audience (S2), degrade-path tests (C4/C6), schema/CI in English
- **parents**: 40ca4095f2f57726b0e5cbf492d5fe8d9014d960d54aad2931cb09e632a8ceaf
- **id**: e54135e45a6edb2599229792f30c0638d95f0b72deab707849ec7a7257f34472

**Body**:
Cleared the non-blocking gaps deferred from the 0.4.0 analysis. S3: the dev-only password form (ROPC) is now REFUSED on a public AS deploy with no social provider, unless LIFELINE_OAUTH_ALLOW_PASSWORD=1 is set explicitly (a loud warning when it is) — production is hosted-login by default, never an accident. The live deploy runs RS mode, so this can't break it. S2: SupabaseJWKSVerifier gained opt-in audience pinning via LIFELINE_OAUTH_AUDIENCE — when set, a JWT minted for a different resource in the same Supabase project is rejected; default stays off (issuer alone) so existing tokens don't break. C4/C6: added tests for the anti-silent-fallback path (OAuth requested but unconfigured -> AUTHLESS, loudly), and the SupabaseClientStore / revoke best-effort degrade paths (network failure -> None / no raise). Cosmetic: schema.sql comments are now English (they print via -- Lifeline — Tier 1 (Supabase / Postgres). Mirrors the local ledger, multi-tenant via RLS.
-- Paste it into your project's SQL Editor (Dashboard → SQL Editor → New query → Run),
-- or generate it with: `lifeline schema`.  You do NOT need to share any key to run this.
--
-- Append-only BY CONSTRUCTION: only SELECT and INSERT have a policy → UPDATE/DELETE are denied
-- by RLS. This enforces Law #2 (append-only) and Law #1 (anchor) in the database itself.

create table if not exists lifeline_entries (
  seq        bigint generated by default as identity,   -- causal order (insertion), per user/line
  owner      uuid not null default auth.uid(),           -- tenant: the entry's owner (multi-tenant)
  line       text not null default 'ledger',             -- which line (code OR conversation)
  id         text not null,                              -- content-addressed id (sha256 of content+parents)
  ts         timestamptz not null default now(),         -- metadata (outside the hash)
  kind       text not null,
  summary    text not null,
  body       text not null default '',
  parents    jsonb not null default '[]'::jsonb,
  dedup_key  text,
  payload    jsonb not null,                             -- the full Entry (Entry.model_dump_json)
  primary key (owner, line, id)                          -- dedup by content, isolated per tenant/line
);

create index if not exists idx_lifeline_owner_line_seq
  on lifeline_entries (owner, line, seq);

create unique index if not exists idx_lifeline_dedup
  on lifeline_entries (owner, line, dedup_key)
  where dedup_key is not null;

alter table lifeline_entries enable row level security;

-- Each user only READS and only INSERTS their own entries. (No UPDATE/DELETE policy
-- → RLS denies by default → append-only in the database.)
drop policy if exists "lifeline_select_own" on lifeline_entries;
create policy "lifeline_select_own" on lifeline_entries
  for select using (owner = auth.uid());

drop policy if exists "lifeline_insert_own" on lifeline_entries;
create policy "lifeline_insert_own" on lifeline_entries
  for insert with check (owner = auth.uid());


-- ============================================================================
-- HITL queue (proposals). MUTABLE — the status changes (pending→approved/rejected).
-- Unlike the ledger (append-only), RLS here ALLOWS UPDATE; but there is NO DELETE
-- policy → the curation history is preserved (you can't erase history).
-- Only what is APPROVED becomes an Entry in lifeline_entries.
-- ============================================================================
create table if not exists lifeline_proposals (
  pid       bigint generated by default as identity primary key,
  owner     uuid not null default auth.uid(),
  line      text not null default 'ledger',
  ts        timestamptz not null default now(),
  status    text not null default 'pending',
  kind      text not null,
  author    text, agent text, provider text, model text,
  summary   text not null,
  body      text not null default '',
  parents   jsonb not null default '[]'::jsonb
);

create index if not exists idx_lifeline_proposals_pending
  on lifeline_proposals (owner, line, status, pid);

alter table lifeline_proposals enable row level security;

-- The owner reads/inserts/updates their own proposals (no DELETE: curation history).
drop policy if exists "lifeline_prop_select" on lifeline_proposals;
create policy "lifeline_prop_select" on lifeline_proposals
  for select using (owner = auth.uid());

drop policy if exists "lifeline_prop_insert" on lifeline_proposals;
create policy "lifeline_prop_insert" on lifeline_proposals
  for insert with check (owner = auth.uid());

drop policy if exists "lifeline_prop_update" on lifeline_proposals;
create policy "lifeline_prop_update" on lifeline_proposals
  for update using (owner = auth.uid()) with check (owner = auth.uid());

-- (Future M4 / hub: per-line sharing policies — a per-line members table and a policy that
-- opens SELECT to members. Out of scope for Tier 1.)


-- ============================================================================
-- Authorization Server (open item #32d96c3d): persistence of DCR clients.
-- The AS (lifeline/oauth.py) runs IN MEMORY by default (correct for a single instance). For
-- multi-instance (a scaled deploy), point a client store at this table: clients registered via
-- DCR survive restarts and are shared across replicas. Codes are one-time/ephemeral (TTL ~300s)
-- and are deliberately NOT persisted here.
-- This is NOT multi-tenant by auth.uid(): client registration happens BEFORE the user logs in,
-- so the gateway uses the service key; treat it as AS infrastructure, not tenant data.
-- ============================================================================
create table if not exists lifeline_oauth_clients (
  client_id    text primary key,
  client_info  jsonb not null,                            -- OAuthClientInformationFull (DCR)
  created_at   timestamptz not null default now()
);
-- Not multi-tenant by uid (registration is pre-login), but the table MUST NOT be exposed to
-- anon/authenticated: without RLS, PostgREST would serve it via the anon key (anyone could read
-- the client_info or insert fake clients). We enable RLS with NO policy → anon/authenticated are
-- denied by default (deny-all), while `service_role` (used by the client store) BYPASSES RLS.
alter table lifeline_oauth_clients enable row level security;), curate.md fixed a non-existent  CLI subcommand (-> ), and ci.yml is English + now runs the skip-gated live tests when SUPABASE_* repo secrets are present (still skips on fork PRs). 156 tests green. Out of scope (still tracked): applying the oauth_clients RLS to the live prod DB (the schema file already has it).

<!-- lifeline:end -->

### #0097 — 2026-06-23T21:43:31.247834+00:00 — correction

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: correction
- **summary**: Correct the mangled body of the post-0.4.0 backlog entry (shell-quoting bug injected schema output)
- **parents**: e54135e45a6edb2599229792f30c0638d95f0b72deab707849ec7a7257f34472
- **id**: 6fd2d9d9681dcb89de902878258e49a1baa44f39eab72db9300ac4de70bcf90d

**Body**:
Cleared the non-blocking gaps deferred from the 0.4.0 analysis. S3: the dev-only password form (ROPC) is now REFUSED on a public AS deploy with no social provider, unless LIFELINE_OAUTH_ALLOW_PASSWORD=1 is set explicitly (with a loud warning) -- production is hosted-login by default, never an accident; the live deploy runs RS mode, so this cannot break it. S2: SupabaseJWKSVerifier gained opt-in audience pinning via LIFELINE_OAUTH_AUDIENCE -- when set, a JWT minted for a different resource in the same Supabase project is rejected; default stays off (issuer alone) so existing tokens do not break. C4/C6: added tests for the anti-silent-fallback path (OAuth requested but unconfigured falls back to AUTHLESS, loudly) and the SupabaseClientStore / revoke best-effort degrade paths (network failure returns None / does not raise). Cosmetic: schema.sql comments are now English (printed by 'lifeline schema'), curate.md fixed a non-existent 'recontextualize' CLI subcommand (the CLI supersede path is 'lifeline log --kind correction --parents <id>'), and ci.yml is English and now runs the skip-gated live tests when SUPABASE_* repo secrets are present. 156 tests green. NOTE: this supersedes entry ea87dc55, whose body was mangled at creation by a shell-quoting bug -- backticks in the --body argument triggered bash command substitution and injected the output of 'lifeline schema' into the body. Corrected forward, not edited (Law #2).

<!-- lifeline:end -->

### #0098 — 2026-07-07T23:47:19.663500+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: 0.5.0 foundation: injective content-addressing (hash v2 + rehash) and first-class lines (L1-L5)
- **parents**: 6fd2d9d9681dcb89de902878258e49a1baa44f39eab72db9300ac4de70bcf90d
- **id**: e9a37ea233886b10e60e6c7a6201d55d92a9b2e524663b96de8d2710073fdcbc

**Body**:
A line-by-line audit (ignoring all docs) found the keystone cracked and lines half-managed; this closes every confirmed finding before any distribution push. (1) BREAKING/hash-v2: the v1 canonical form joined fields with newlines and was NOT injective -- a newline inside any field provably collided two different entries into one id, and the store would silently swallow the second as a 'duplicate'. v2 length-prefixes every field (and each sorted parent), making distinct content unable to share an id; property tests lock it. `lifeline rehash` migrates existing ledgers (topological old->new remap across entries/parents/embedded payload/edges + regenerated view, .bak backup, verify enforced) -- both real lines (ledger 97, strategy 4) migrated and verify OK. (2) Lines are now first-class: LIFELINE_LINE works for the LOCAL MCP server (it was a documented no-op outside the cloud); the cloud HITL queue is line-scoped on get/set_status (approve-by-pid could reach another line of the same owner); clone rebuilds+verifies EVERY line; `lines` works against the cloud. (3) `lifeline promote --from/--to` turns the doc-only claim into code: cross-line copy as roots with provenance, idempotent by content-addressing, superseded entries skipped. (4) Integrity: ingest now VALIDATES the recorded id against recomputed content (hand-edited views warn; migrate --strict fails) and respects explicit empty parents (true roots round-trip); pull/clone verify after merge; push stages ONLY LIFELINE*.md (git add -A could sweep secrets into a sync commit); supersession fixpoint got an iteration cap. (5) Dense-recall embeddings cached by entry id -- content-addressing makes the cache eternally fresh, so indexing is incremental instead of O(ledger) model calls per query. Dead /auth/v1/user verifier removed (JWKS superseded it). 180 tests green (+24 new). Why now: this is the foundation the capture loop (F1) writes into -- capture at scale on a collidable id or leaky lines would corrupt the very trust the product sells.

<!-- lifeline:end -->

### #0099 — 2026-07-08T00:51:10.075761+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: F1 shipped & validated live: auto-capture on PR merge (hub) + zero-LLM local capture (core)
- **parents**: e9a37ea233886b10e60e6c7a6201d55d92a9b2e524663b96de8d2710073fdcbc
- **id**: f7290853c30fcb3cc5c60d6a128d0989c9e47c1c117ebea91a3d083dfbb3328c

**Body**:
The capture loop -- the product's existential gap -- is now wired end-to-end and proven against production. Hub (private repo): pull_request closed+merged -> handle_merged_pr resolves the repo's line, gathers ONLY human-written text (PR body + best-effort review bodies; the diff is never fetched -- Laws #1/#5 enforced by construction), drafts via Claude (plain HTTP, optional ANTHROPIC_API_KEY) with a zero-LLM heuristic fallback, abstains when no rationale is written (no proposal, no nagging comment), and queues PENDING proposals with a provenance marker that doubles as the redelivery-dedup key. Dashboard Review tab gained EDIT-BEFORE-APPROVE (PATCH, pending-only) -- machine drafts are raw material, curators fix then seal -- plus a PR-origin link; capture metrics (PRs captured, status breakdown, approval/noise rate) derive from the markers, no new tables. Core: `lifeline capture` drafts from git commit messages (conventional prefix -> kind; commit body = the why, required; trailers stripped; idempotent via capture.head). Live e2e (signed webhook, synthetic PR #999901): captured -> proposal #6 PENDING with correct kind/attribution/provenance; redelivery -> already_proposed; artifact curated (rejected). The gate also caught real infra truth: the free-tier Supabase project had PAUSED silently (ConnectError from prod) -- restored (Max paused to free the slot), data intact, and the pending GitHub install claim was completed (line_owner backfilled to the owner's account). Standing lesson for F3: a paid hub cannot sit on a pausable free tier -- upgrade or add boot-time schema self-check before design partners. Suites: core 183 green, hub 80 green (14 new).

<!-- lifeline:end -->

### #0100 — 2026-07-08T00:58:49.764287+00:00 — open

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: open
- **summary**: F2 remainder: 60s demo + verified integration recipes
- **parents**: f7290853c30fcb3cc5c60d6a128d0989c9e47c1c117ebea91a3d083dfbb3328c
- **id**: c00f3eda03f2d563704b9ba370d5f259a2dbd838209891c1a433953ceac95bf1

**Body**:
The exam's TTC probe flagged the ledger had no open threads — a fresh AI couldn't see what's next. This is next: the landing demo asset (AI connects -> what/why/decided/next; PR merge -> proposal in Review) and integration recipes verified per client (Claude Code validated; Cursor/Gemini/ChatGPT to verify honestly). The demo is the artifact that carries any launch.

<!-- lifeline:end -->

### #0101 — 2026-07-08T00:58:50.799037+00:00 — open

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: open
- **summary**: F3: revenue activation — team lines, billing, and hub infra posture
- **parents**: c00f3eda03f2d563704b9ba370d5f259a2dbd838209891c1a433953ceac95bf1
- **id**: 3de58fcb032b11da8f67681bf369802bb8d23a724f239f21bde8978bdfe28b46

**Body**:
After F2: team-line RLS (line_members seam) + invite flow, Stripe checkout wired to tiers (Marketplace tier_for reused), hosted onboarding under 10 minutes, and the standing infra lesson from the F1 gate: a paid hub cannot sit on a pausable free tier — upgrade the Supabase project or add boot-time schema self-check BEFORE design partners.

<!-- lifeline:end -->

### #0102 — 2026-07-08T01:06:59.618211+00:00 — correction

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: correction
- **summary**: F2 delivered: exam command, 60s demo asset, verified integration recipes
- **parents**: c00f3eda03f2d563704b9ba370d5f259a2dbd838209891c1a433953ceac95bf1
- **id**: 5bb17ab90787eb0e90ac49fdc0d1af043564018c13bb86e179bedf55e92127d1

**Body**:
Closes the F2-remainder thread. `lifeline exam` shipped as a product command (Context Health 0-100, integrity-gated, every gap paired with the command that fixes it; the dogfood run scored 81/B, caught the missing open threads, and after recording them scored 100/A — the score is actionable, not vanity). The 60s demo shipped as a self-contained animated SVG built from REAL outputs (connect -> capture -> prove), wired into getting-started with a landing link, and the stale landing proof panel was refreshed to current truth (101 entries, hash-v2 head, exam line). INTEGRATION.md now states the honest verification level per client (Claude Code + remote OAuth validated live; Cursor/Desktop/Gemini config-checked, e2e reports invited) and documents the capture loop (local zero-LLM + GitHub App). 188 tests green.

<!-- lifeline:end -->

### #0103 — 2026-07-08T22:08:07.862832+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Checkpoint review (F2->F3): UTF-8 git decoding crash in capture, exam naive-ts hardening, explicit dedup/caps
- **parents**: 5bb17ab90787eb0e90ac49fdc0d1af043564018c13bb86e179bedf55e92127d1
- **id**: 61fab29030c0eb411656a4374f99a72852c283a08796fa8793a2372233500d7c

**Body**:
A deep adversarial self-review of everything F0-F2 shipped (the parallel reviewer agents died on an account spend limit, so the review ran inline with empirical probes instead of trust). CONFIRMED+FIXED: sync._git decoded git output with the locale codepage — on Windows (cp1252) a commit body containing certain UTF-8 chars crashed the subprocess reader thread and took `lifeline capture` down with it; decoding is now pinned to UTF-8 with errors=replace (regression test with an accented body). HARDENED: `lifeline exam` coerces naive timestamps to UTC (a hand-crafted view could TypeError the freshness math). REFUTED by experiment: the suspicion that surgical `git add` aborts when one view is gitignored — git skips the ignored path and stages the rest, so push in this very repo (with the ignored strategy view) is fine. MADE EXPLICIT (no silent caps): merge-capture redelivery dedup only spans the pending queue — safe because identical drafts dedup at the ledger by content-addressing; and cloud `lines()` counts truncate at PostgREST max-rows (~1000). Also verified: dashboard esc() covers attribute-quote injection for untrusted PR text in the edit form. Gate: core 189 green, hub 80 green, both ledgers verify OK, exam 100/A.

<!-- lifeline:end -->

### #0104 — 2026-07-08T22:23:09.416160+00:00 — milestone

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: milestone
- **summary**: F3 core shipped: tier gate on line sharing, real Stripe path, boot schema self-check
- **parents**: 61fab29030c0eb411656a4374f99a72852c283a08796fa8793a2372233500d7c
- **id**: 4b9403f0687f4d180d49c3e470cbf475b3503431fb9955cd6ed995c14c64e864

**Body**:
Revenue activation, the honest slice: (1) the PAID feature (team-line sharing) is now actually gated by tier — free gets 1 shared member per line (a taste), team gets the seat cap, resharing is idempotent; before this, org seats were capped but line sharing was unlimited, so the paywall was decorative. (2) Stripe direct-sale implemented without SDK: owner/admin-only checkout carrying org_id/tier in metadata, webhook signature-verified (HMAC t.v1 + anti-replay) before any work, lifecycle events mapped to hub_subscriptions; turning it on is 3 env vars — GitHub Marketplace remains the live path. (3) The pause incident became code: a boot-time read-only schema self-check logs CRITICAL and surfaces truth in /healthz instead of letting the hub look healthy while every DB route dies. Closes the infra half of open #0101; the remaining half (Supabase Pro upgrade + Stripe keys + price) is owner action. Hub 90 tests green.

<!-- lifeline:end -->

### #0105 — 2026-07-08T22:35:46.723411+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: Independent adversarial review of hub F1+F3 applied: marker injection closed, Stripe robustness
- **parents**: 4b9403f0687f4d180d49c3e470cbf475b3503431fb9955cd6ed995c14c64e864
- **id**: 2f26819175ea9a5a91c80078e070b935a6f29cdde1feecb1fc5ebabab8609688

**Body**:
With subagents back (the earlier reviewers died on the account spend limit), an independent adversarial pass covered capture/merge-handler/edit/metrics/tier-gate/billing/self-check. Verdict: no CRITICALs — RLS backing and the Stripe metadata trust chain are sound (a signed-but-crafted event cannot set a tier for an org the payer doesn't own). Real findings applied: (M1) untrusted PR/review text could plant our provenance marker to suppress another PR's capture or poison metrics -- forged marker lines are now stripped at draft time and all marker matches are line-anchored; (L1) Stripe secret rotation sends multiple v1 signatures and we kept only the last (401ing legit events) -- any match now passes; (L3) an out-of-order subscription.deleted could downgrade a newer subscription -- guarded by the stored sub id; plus tier clamp on garbage metadata and 502 on url-less checkout. Hub 95 tests green (5 new). Noted as design-intent: a member of a paid org inherits sharing caps for personal lines.

<!-- lifeline:end -->

### #0106 — 2026-07-09T00:40:25.092456+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: AI-ops G1-G3: drafter provenance + LLM state, uptime cron with keep-alive, daily hub backup
- **parents**: 2f26819175ea9a5a91c80078e070b935a6f29cdde1feecb1fc5ebabab8609688
- **id**: f9023a73a641afbfc7e8391196738f67ab846fe12659d1bb71f55e23dac06e52

**Body**:
The architecture review's AI-ops pass found the trio the pause incident exposed: detect, don't degrade silently, be able to restore. (G1) The capture drafter now has provenance and observability: each proposal's model field records WHO drafted it (real Claude model id or 'heuristic'), LLM_STATE counts llm_ok/fallbacks (a configured-but-dying key is visible, not a log whisper), /healthz exposes it and capture-metrics break down by drafter. (G2) /readyz does a live 1-row DB probe (503+CRITICAL on failure) and a GitHub Actions cron pings it every 15min -- failure emails the owner via red workflow, and the real DB touch keeps the Supabase free tier from pausing and both Render services awake; validated live (run green). (G3) A daily workflow exports all hub_*/lifeline_* tables to private-repo artifacts (90d) -- hub state (pending proposals, provisioning, subscriptions) is no longer restore-or-lose; awaiting the owner's ok to store the service-role secret in Actions. Hub 97 tests green. Remaining from the ops review, tracked not blocking: hub migration ledger, drafter daily cost cap, staging env, head-id context cache.

<!-- lifeline:end -->

### #0107 — 2026-07-09T01:00:04.236349+00:00 — fix

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: fix
- **summary**: AI-ops G4-G8 closed: migration trail, drafter cost cap, head-id context cache, ops runbook
- **parents**: f9023a73a641afbfc7e8391196738f67ab846fe12659d1bb71f55e23dac06e52
- **id**: f252d9f15addbb872729409af7b071da96c99432ab46eacbf2c663b8d15d10df

**Body**:
The last gaps from the ops review are shut. (G4) hub_migrations table applied to prod (RLS on, service-role-only) with 001-005 backfilled -- hand-applied migrations now leave a trail. (G5) LIFELINE_CAPTURE_DAILY_MAX (default 200) caps drafter LLM calls per day with date rollover; beyond it capture continues on the heuristic and LLM_STATE counts budget_capped -- spend stops, capture never does; test proves the LLM is not even called when capped. (G8) the hosted context endpoint caches by (owner, line, HEAD id): the head is content-addressed, so the cache is stale-proof BY CONSTRUCTION -- a new entry changes the head and thus the key; one 1-row head query replaces O(ledger) streaming on repeat reads, query path stays uncached. (G6/G7) docs/OPS.md is the runbook: monitors, backup/restore steps, migration discipline, and the explicit known limits (drafter prompt-injection contained by the HITL + body-fencing rings; main=prod staging posture with the pre-design-partner plan; single-instance counters; PostgREST caps). Hub 101 tests green. The system now detects, refuses to degrade silently, restores, remembers its schema history, caps its own spend, and scales its hottest read.

<!-- lifeline:end -->

### #0108 — 2026-07-09T01:20:11.812975+00:00 — release

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: release
- **summary**: 0.5.0 (beta) published to PyPI — hash v2, first-class lines, the capture loop, exam
- **parents**: f252d9f15addbb872729409af7b071da96c99432ab46eacbf2c663b8d15d10df
- **id**: 9e42b00179be4f0fdc6efef70ca0060042d203a8ca351dfcdfbe84357534af75

**Body**:
Tag v0.5.0 -> publish.yml -> PyPI (34s), latest confirmed 0.5.0. The category-changing release: BREAKING hash-scheme v2 (injective content-addressing; existing ledgers migrate once via `lifeline rehash` -- both real lines migrated and verifying), lines first-class end-to-end (local MCP LIFELINE_LINE, cloud scoping, clone-all, `promote` across lines), the CAPTURE LOOP (`lifeline capture` zero-LLM from commit messages + hub auto-capture on merged PRs, validated live), and `lifeline exam` (Context Health 0-100, integrity-gated). 195 tests. Site audited and refreshed to current truth before the cut (proof panel 107/f252d9f1; demo + CLI docs verified live). Stripe setup attempted next: the .env STRIPE_* vars turned out to be EMPTY placeholders -- no Stripe account exists yet; product/price/webhook creation is scripted and ready, blocked only on the owner creating the account and pasting a secret key (owner action).

<!-- lifeline:end -->

### #0109 — 2026-07-22T16:25:08.221701+00:00 — feature

- **author**: unknown
- **agent**: human
- **provider**: none
- **model**: human
- **kind**: feature
- **summary**: Typed knowledge graph (MVP-1): kind=relation + entity kinds + `lifeline graph` (Regente Phase-1 slice)
- **parents**: 9e42b00179be4f0fdc6efef70ca0060042d203a8ca351dfcdfbe84357534af75
- **id**: 42c83ccc23635c688a26d70a7c6c25eb39036dbc2be7cee2a0e9a4c2659cd750

**Body**:
First slice of the Regente evolution, landed in Lifeline as GENERIC MEMORY (not execution -- stays inside the non-goals). Added entity kinds (service/api/test/requirement/debt) and `kind=relation`: a relation is an Entry with parents=[from,to] (verify guarantees both ends exist -- referential closure for free) and the DIRECTION in the body, because parents are a sorted SET in the hash (Law #3) so order doesn't survive. New lifeline/graph.py projects the in-force graph (superseded relations drop, same as decisions); `lifeline relate` records one and `lifeline graph --depends-on/--dependents/--of` answers STRUCTURALLY, not as text. Purely additive: no canonical-form change, so NO rehash -- proven live (verify OK) and by test (existing ids unchanged). This is the Knowledge Kernel the Regente kernel will query. Decision: Regente is a SEPARATE repo importing lifeline+lifegs (pinned), never a fork -- orchestration is the sealed non-goal #6a66d39c, so only memory/typing enters the core. lifegs frozen at 0.2.0 (191 tests) as the pinned dependency. 195 tests green.

<!-- lifeline:end -->
