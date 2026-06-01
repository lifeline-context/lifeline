# Deploy — conector AUTHLESS pro claude.ai (validação)

Objetivo: provar o **one-click** ("conecto e o claude.ai já sabe o contexto do projeto") **sem
construir AS** — usando o modo authless que o claude.ai aceita. É o passo de **validação**;
multi-tenant pago vem depois com o AS (#0049). Pesquisa que embasa: line #0052.

## ⚠️ Segurança (leia antes)
Authless + endpoint público = **qualquer um com a URL lê o contexto** e pode **enfileirar
propostas**. Mitigações reais:
- A escrita é **HITL**: a IA só **propõe** (pendente); nada entra na line sem você aprovar.
  O pior que um intruso faz é **sujar a fila de propostas** (você rejeita) — não corrompe a line.
- Use uma **line não-sensível** (este demo expõe a própria LIFELINE.md do projeto — pública no
  GitHub de qualquer forma) e uma URL difícil de adivinhar.
- **NÃO use authless com dado privado/real.** Pra isso é multi-tenant + AS (#0049).

## Smoke local (30s, antes de deployar)
```bash
pip install -e ".[cloud]"
LIFELINE_MCP_TRANSPORT=streamable-http lifeline-mcp-remote     # serve em http://0.0.0.0:8000/mcp
# noutro terminal, conecte pelo Claude Code (CLI aceita URL direta):
claude mcp add --transport http lifeline http://127.0.0.1:8000/mcp
```
Se o `lifeline context` aparece como resource no cliente, está funcionando.

## Deploy (free tier — escolha um)
A imagem (`Dockerfile`) reconstrói o `.db` da `LIFELINE.md` no boot e serve authless.

- **Railway:** New Project → Deploy from Repo → detecta o `Dockerfile` → deploy → copie a URL pública.
- **Render:** New → Web Service → Docker → aponte o repo → Create → copie a URL.
- **Fly.io:** `fly launch` (usa o `Dockerfile`, não adicione DB) → `fly deploy` → `fly open`.

O endpoint fica em `https://<seu-host>/mcp` (streamable-http). Pra SSE, suba com
`LIFELINE_MCP_TRANSPORT=sse` → `https://<seu-host>/sse`.

## Registrar no claude.ai (o clique é seu)
1. claude.ai → **Settings → Connectors → Add custom connector**.
2. Cole `https://<seu-host>/mcp` · **Authentication: None** (authless) · Save.
3. Numa conversa, habilite o conector. O resource `lifeline://project/context` e as tools
   (`lifeline_recall`, e as de escrita **HITL** `lifeline_append`/`recontextualize`) aparecem.
4. Pergunte algo do projeto — o claude.ai responde pelo contexto da line. **Esse é o teste.**

## Quando for além da validação
Multi-tenant (cada usuário a sua line) → ligue `LIFELINE_OAUTH=1` + um AS (provedor gerenciado
com DCR, ou shim). O **Resource Server já está pronto** (`docs/MCP_REMOTE.md`); falta só o AS (#0049).
