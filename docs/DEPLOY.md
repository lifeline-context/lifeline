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

## Deploy no Render (recomendado — $0, usa o `Dockerfile`)
A imagem reconstrói o `.db` da `LIFELINE.md` no boot e serve authless. Duas formas:

**A) Blueprint (lê o `render.yaml`, menos cliques):**
1. [render.com](https://render.com) → sign up (login GitHub).
2. **New → Blueprint** → conecte o repo `jessianmart/lifeline` → ele lê o `render.yaml` → **Apply**.

**B) Manual:**
1. **New → Web Service** → conecte o repo → **Runtime: Docker** → **Instance Type: Free** → **Create**.

Em ambos, espere o build terminar. A URL fica `https://<seu-serviço>.onrender.com`.

**Confirme que subiu:** abra `https://<seu-serviço>.onrender.com/healthz` no navegador → deve mostrar **`ok`**.

⚠️ **Free tier dorme após 15 min ocioso.** O 1º acesso do claude.ai acorda o serviço (~1 min) —
se a 1ª tentativa der timeout, tente de novo. Pra sempre-on (sem cold start): troque pra
**Starter ($7/mês)** no `render.yaml` (`plan: starter`) ou no dashboard. (Railway $5/mês é a
alternativa quando aprovarmos a viabilidade.)

> Teste local antes (opcional, se sua rede deixar): `lifeline-mcp-remote` + um túnel
> (`npx cloudflared tunnel --url http://127.0.0.1:8000`). ⚠️ Cuidado: muitas redes **bloqueiam
> a porta 7844** do cloudflared (a nossa bloqueava) — se o túnel cair, é a rede; o Render resolve.

## Registrar no claude.ai (o clique é seu)
1. claude.ai → **Settings → Connectors → Add custom connector**.
2. Cole `https://<seu-host>/mcp` · **Authentication: None** (authless) · Save.
3. Numa conversa, habilite o conector. O resource `lifeline://project/context` e as tools
   (`lifeline_recall`, e as de escrita **HITL** `lifeline_append`/`recontextualize`) aparecem.
4. Pergunte algo do projeto — o claude.ai responde pelo contexto da line. **Esse é o teste.**

## Quando for além da validação
Multi-tenant (cada usuário a sua line) → ligue `LIFELINE_OAUTH=1` + um AS (provedor gerenciado
com DCR, ou shim). O **Resource Server já está pronto** (`docs/MCP_REMOTE.md`); falta só o AS (#0049).
