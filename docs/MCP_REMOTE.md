# MCP remoto (HTTP/SSE) — a superfície da nuvem

A **mesma** superfície MCP do modo local, servida por HTTP — pra uma IA conectar de fora
(não só via stdio). Recursos/tools idênticos, escrita **continua HITL**:

- **Ler:** resource `lifeline://project/context` + tool `lifeline_recall`.
- **Propor (HITL):** tools `lifeline_append` / `lifeline_recontextualize` → entram como
  PENDENTES; um humano aprova (`lifeline review`/`approve`) antes de entrar na line.

Backend escolhido por env (mesmo factory da CLI): SQLite local **ou** Supabase (nuvem).

## Rodar

```bash
# nuvem (multi-tenant via RLS) — precisa do schema aplicado (cloud/schema.sql)
export LIFELINE_STORE=supabase
export SUPABASE_URL=https://rzphncyjrilhwpuemrcl.supabase.co
export SUPABASE_KEY=<apikey do projeto>      # NÃO comite — use .env
export SUPABASE_TOKEN=<access token JWT>      # escrita sob RLS
export LIFELINE_MCP_HOST=0.0.0.0 LIFELINE_MCP_PORT=8000
lifeline-mcp-remote
```

- Transporte: `LIFELINE_MCP_TRANSPORT=sse` (default) → endpoints `GET /sse` + `POST /messages`;
  ou `streamable-http` → `/mcp`.
- Backend local (sem nuvem): omita `LIFELINE_STORE` → SQLite (`LIFELINE_DB`).
- Line: `LIFELINE_LINE=<nome>` (default `ledger`).

## Deploy (zero-custo, honesto)

É um servidor **Python** (FastMCP + uvicorn/starlette). **NÃO** roda em Supabase Edge
Functions (essas são Deno/TypeScript). Rotas de custo-zero/baixo:

- **Fly.io / Render / Railway** (free tier) — um processo `lifeline-mcp-remote` com as env
  vars; o Supabase continua sendo o store.
- **Container** próprio (`pip install lifeline-context[cloud]` + as env vars).
- Dev/local exposto por túnel (cloudflared/ngrok) pra testar rápido.

O Supabase segue de graça como **store** (Postgres+RLS); o host só roda o processo MCP.

## OAuth / multi-tenant (Resource Server) — `LIFELINE_OAUTH=1`

Ligue com `LIFELINE_OAUTH=1` (+ `LIFELINE_STORE=supabase` + `SUPABASE_URL`/`KEY`). O servidor
vira um **OAuth 2.1 Resource Server**:

- Exige `Authorization: Bearer <JWT do usuário>` em cada requisição; valida contra o Supabase
  (`/auth/v1/user`). Inválido/expirado → **401**.
- Escopa o store pelo **JWT daquele usuário** → multi-tenant real via RLS (`owner=auth.uid()`):
  cada usuário só vê/propõe na própria line. (Sem `LIFELINE_OAUTH`, é single-tenant via o
  `SUPABASE_TOKEN` do ambiente.)
- Publica o **discovery** em `GET /.well-known/oauth-protected-resource` (RFC 9728), apontando
  o Authorization Server (`LIFELINE_OAUTH_ISSUER`, default `…/auth/v1`).

```bash
export LIFELINE_OAUTH=1 LIFELINE_STORE=supabase
export SUPABASE_URL=… SUPABASE_KEY=<apikey>
export LIFELINE_MCP_PUBLIC_URL=https://seu-host   # url pública (vai no metadata)
lifeline-mcp-remote
```

**Conectar agora pelos CLIs (NÃO pelos apps web):** o **Claude Code** e o **Gemini CLI** aceitam
token por header — ex.: `claude mcp add --transport sse lifeline https://seu-host/sse --header "Authorization: Bearer <jwt>"`.
⚠️ **O claude.ai web e o ChatGPT NÃO aceitam Bearer estático** (`static_bearer` não suportado);
nos apps hospedados é **authless** ou **OAuth** — ver abaixo.

## Conectar nos apps web (claude.ai / ChatGPT) — o que a pesquisa confirmou (jun/2026)

- **claude.ai aceita conector AUTHLESS** (`auth: "none"`) → dá pra ter "conectar em um clique"
  **sem AS nenhum** — mas **sem identidade por usuário** (serve p/ single-tenant / line
  compartilhada, não p/ multi-tenant). Ótimo pra **validar** o valor antes de investir no AS.
- **Multi-tenant (cada um vê o seu) exige um Authorization Server** (authorize+token+PKCE+
  metadata). **MAS DCR NÃO é obrigatório:** o claude.ai aceita **CIMD** ou **client
  pré-registrado** (creds via `mcp-review@anthropic.com`); o ChatGPT aceita CIMD/clients
  predefinidos. DCR só elimina o setup manual.
- **Bearer estático não serve** nos apps web (só nos CLIs). ChatGPT exige **Developer Mode**
  (planos pagos; o free não tem).
- **AS zero-custo com DCR (quando for construir):** Cloudflare `workers-oauth-provider` (OSS,
  free Workers), Keycloak (OSS, self-host), Stytch (free ~10K MAU). **Pegadinha de integração:**
  o AS precisa render identidade compatível com a RLS do Supabase (`auth.uid()`) — o mais limpo é
  o AS usar o Supabase Auth como login, ou re-plugar o RS no JWKS do provedor.

> Resumo: o **Resource Server** (validação + metadata + multi-tenant) está pronto e testado.
> Pro one-click hospedado — **authless valida sem AS**; multi-tenant **precisa de AS, não de DCR**.
> (Pesquisa ancorada na line #0052; próximo passo do AS = #0049.)

Em todos, **o nosso RS não muda** — ele já valida o JWT e escopa por usuário.

## Segurança

Credenciais só via ambiente (`.env`, gitignored) — nunca em commit. Escrita sempre HITL:
a IA remota **propõe**, o humano cura. O servidor não expõe `approve`/`reject` (curadoria
é local/confiável), nem os comandos de git (`push/pull/clone`).
