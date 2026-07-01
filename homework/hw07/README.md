# HW07 — CVE Intelligence Assistant (Open WebUI + RAG + live tool)

Course assignment: a self-hosted assistant that answers **historical** CVE questions from a
Kaggle knowledge base and **live** CVE-risk questions from a local tool server.

```
Open WebUI ── KB (Kaggle CVE CSV)            → historical / static questions
      │
      └────── OpenAPI tool → tools_server.py → live CVE API  → current-risk questions
                                                (RapidAPI, or free Shodan CVEDB fallback)
```

## Layout

| File | Purpose |
|------|---------|
| [`owui_kb_setup.py`](owui_kb_setup.py) | Idempotently create OWUI KB and upload CSV (REST API). |
| [`tools_server.py`](tools_server.py) | FastAPI: `GET /cve/{id}` live lookup, OpenAPI at `/openapi.json`. |
| [`docker-compose.yml`](docker-compose.yml) | OWUI + Ollama stack with RAG env vars. |
| [`data/download_dataset.py`](data/download_dataset.py) | Download CVE CSV from Kaggle (idempotent). |
| [`AGENTS.md`](AGENTS.md) | Build plan for Cursor agent. |
| [`CURSOR_PROMPT.md`](CURSOR_PROMPT.md) | One-shot agent prompt. |

## Quickstart (Windows)

```powershell
cd homework\hw07

# 1. Stack
docker compose up -d
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1

# 2. Python deps + secrets
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # fill OWUI_API_KEY (+ optional RapidAPI)

# 3. Dataset (requires KAGGLE_API_TOKEN in repo root .env)
python data\download_dataset.py

# 4. Knowledge base
python owui_kb_setup.py --csv .\data\cve.csv --name "CVE Intelligence" `
  --description "Historical CVE / CVSS records for RAG"

# 5. Tool server (host)
uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload
curl http://localhost:5005/health
curl http://localhost:5005/cve/CVE-2021-44228
```

Or use scripts:

```powershell
.\scripts\start_stack.ps1
.\scripts\start_tool_server.ps1
```

## Open WebUI wiring

1. **Admin → Settings → External Tools → Add OpenAPI server**
   - URL: `http://host.docker.internal:5005/openapi.json` (Docker OWUI → host tool server)
2. **Workspace → Models →** attach **CVE Intelligence** KB to a tool-capable model (`llama3.1`).
3. Enable native function calling on the model.

## Demo prompts (prove KB vs live split)

| Path | Example question |
|------|------------------|
| **KB** | "Which CVEs in my dataset affected Apache Struts, and their CVSS scores?" |
| **Tool** | "What is the current EPSS score and KEV status for CVE-2021-44228?" |

## Environment

Copy [`.env.example`](.env.example) → `.env` (gitignored). Repo root [`.env.example`](../../.env.example)
also documents shared keys (`KAGGLE_API_TOKEN`, `RAPIDAPI_KEY`).

| Variable | Required | Purpose |
|----------|----------|---------|
| `OWUI_API_KEY` | KB upload | Open WebUI → Settings → Account → API Keys |
| `RAPIDAPI_KEY` + `RAPIDAPI_HOST` | Optional | Live CVE via RapidAPI; omit to use Shodan CVEDB |
| `KAGGLE_API_TOKEN` | Dataset | Repo root `.env` for Kaggle MCP / download script |

## MCP (optional local overrides)

Root [`.mcp.json`](../../.mcp.json) includes `kaggle`. For Open WebUI MCP during setup, copy
[`mcp.json.example`](mcp.json.example) blocks into gitignored `.cursor/mcp.json` — never commit keys.

## Tests

```powershell
cd homework\hw07
python -m pytest tests/ -q
```

CI runs `hw07-tools-server` offline (mocked HTTP — no live API keys).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tool works in curl, fails in OWUI | Use `host.docker.internal:5005`, not `localhost` |
| KB upload 401 | Regenerate `OWUI_API_KEY` in Open WebUI settings |
| KB upload 404 on endpoint | Check `http://localhost:3000/docs` for your OWUI version |
| Port 3000 in use | `docker stop open-webui` then `docker compose up -d` here |
| RapidAPI 404 | Leave `RAPIDAPI_*` blank — server falls back to Shodan CVEDB |
