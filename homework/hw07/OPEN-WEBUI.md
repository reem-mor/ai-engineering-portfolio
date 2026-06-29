# Open WebUI — Manual Setup Runbook (HW07)

Step-by-step guide for Knowledge Base upload and tool server registration.
Open WebUI runs in **Docker** on port **3001** (see [`docker-compose.yml`](../docker-compose.yml)); the tool server runs on the **host** at port 5005.

## Prerequisites checklist

- [ ] Ollama installed and a model pulled (`ollama pull llama3.2:3b`)
- [ ] Docker Desktop running
- [ ] `netflix_titles.csv` in [`../data/`](../data/)
- [ ] Tool server running: `uvicorn tools_server:app --host 0.0.0.0 --port 5005`
- [ ] `curl http://localhost:5005/health` returns `{"status":"ok",...}`

## Step 1 — Start Open WebUI

```powershell
cd homework\hw07
docker compose up -d
```

Open http://localhost:3001 (auth disabled for homework stack). For a personal Open WebUI on `:3000`, adapt URLs accordingly.

## Step 2 — Connect Ollama

1. **Admin Panel → Settings → Connections**
2. Set Ollama base URL: `http://host.docker.internal:11434` (Docker on Windows)
3. Save and verify models appear under **Models**

## Step 3 — Create Knowledge Base

1. **Workspace → Knowledge → + Create Collection**
2. Name: `netflix-shows`
3. Upload `homework/hw07/data/netflix_titles.csv`
4. Wait until status shows indexed / ready
5. **Screenshot:** `screenshots/01-kb-collection-created.png`, `02-kb-csv-uploaded.png`, `03-kb-indexed.png`

## Step 4 — KB chat test

1. Start a new chat
2. Attach/select the `netflix-shows` collection
3. Ask: *"How many rows are type TV Show vs Movie?"*
4. Confirm answer references dataset content (not hallucinated live data)
5. **Screenshot:** `screenshots/04-kb-chat-answer.png`

## Step 5 — Register tool server

1. **Admin → Settings → Integrations → External Tool Servers**
2. URL: `http://host.docker.internal:5005` (must be `http://`, not `https://`)
3. Save — Open WebUI should discover OpenAPI tools from `/openapi.json`
4. **Screenshot:** `screenshots/05-tool-server-configured.png`

### Troubleshooting tool connection

| Symptom | Fix |
|---------|-----|
| Connection refused | Confirm uvicorn binds `0.0.0.0:5005`, not `127.0.0.1` only |
| Wrong host from Docker | Use `host.docker.internal` on Windows Docker Desktop |
| HTTPS pre-filled | Change to plain `http://` |
| CORS errors | Tool server allows localhost Open WebUI origins (`:3000`, `:3001`) |

## Step 6 — Live tool chat test

1. Enable tools in chat (tool icon / model settings)
2. Ask: *"What is the capital of Brazil?"* — should invoke `country_info`
3. Requires `RAPIDAPI_KEY` in tool server `.env`
4. **Screenshot:** `screenshots/06-tool-chat-answer.png`

## Step 7 — Combined demo (optional)

Attach KB **and** enable tools. Ask:

> Compare Netflix content listed for Japan in our dataset with live country info for Japan.

Expect: KB retrieval for dataset facts + tool call for live country data.

## Cleanup

```powershell
docker compose -f homework/hw07/docker-compose.yml down
# Optional: docker volume rm hw07_open-webui-hw07
```

Do not commit Open WebUI sqlite volumes or `.env` files with API keys.
