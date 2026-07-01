# Homework 07 — Open WebUI KB + Live Tools

Local **Open WebUI + Ollama** stack: answer from a **Kaggle CSV Knowledge Base** (historical job-posting skills) and fetch **live job listings** via a **Web UI Tool** → local Python server → **JSearch (RapidAPI)**.

**Design:** The Knowledge Base indexes a static Kaggle CSV so the model can answer aggregate questions about skills, roles, and posting text from the snapshot. The Web UI Tool calls a host-side Python server that wraps JSearch for live job listings. KB handles “what did postings say historically?”; the Tool handles “what is hiring right now in Israel?”

---

## Architecture

```
Kaggle CSV (job_postings.csv)
    → Open WebUI Knowledge Base (ai-job-postings)
    → Chat (llama3.2:3b) — historical / aggregate questions

Open WebUI Tool (hw07_live_job_search / search_live_jobs)
    → http://host.docker.internal:5005
    → tools_server.py (FastAPI on host)
    → JSearch via RapidAPI — live job listings
```

| Component | File / URL |
|-----------|------------|
| KB collection | `ai-job-postings` |
| Tool ID | `hw07_live_job_search` |
| Tool server | [`tools_server.py`](tools_server.py) — `GET /health`, `POST /jobs/search` |
| Open WebUI tool | [`openwebui_tool.py`](openwebui_tool.py) — Valves URL `http://host.docker.internal:5005` |
| JSearch client | [`jsearch_client.py`](jsearch_client.py) |
| Chat model | `llama3.2:3b` (Ollama) |
| Embeddings | `nomic-embed-text` (recommended for KB indexing) |

---

## Prerequisites

- Docker Desktop
- Python 3.12+
- [Kaggle API credentials](https://www.kaggle.com/settings) and [RapidAPI JSearch key](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- GPU optional (`llama3.2:3b` runs well on consumer GPUs)

---

## Quick setup

```powershell
cd homework\hw07
copy .env.example .env
# Fill RAPIDAPI_KEY, KAGGLE_USERNAME, KAGGLE_KEY (or use repo-root KAGGLE_API_TOKEN)
python scripts\verify_env.py
pip install -r requirements.txt
python data\download_dataset.py
docker compose up -d
docker exec hw07-ollama ollama pull llama3.2:3b
docker exec hw07-ollama ollama pull nomic-embed-text
docker compose ps
```

**Terminal B — tool server (host):**

```powershell
cd homework\hw07
.\scripts\start_tool_server.ps1          # live RapidAPI from .env
# or offline:
.\scripts\start_tool_server.ps1 -MockRapidApi
```

Verify:

```powershell
curl.exe http://localhost:3000/health
curl.exe http://localhost:5005/health
```

Expected tool server `/health` (no secrets):

```json
{"status":"ok","mock":false,"jsearch_configured":true}
```

Set `HW07_MOCK_RAPIDAPI=1` in `.env` for offline pytest/screenshots without RapidAPI quota.

---

## Environment variables

Copy [`.env.example`](.env.example) to `.env` — **never commit `.env`**.

| Variable | Purpose |
|----------|---------|
| `RAPIDAPI_KEY` | JSearch API key from RapidAPI (JSearch app subscription) |
| `RAPIDAPI_HOST` | API host only — `jsearch.p.rapidapi.com` (NOT `rapidapi.com`) |
| `RAPIDAPI_BASE_URL` | Documentation only — client builds `https://{RAPIDAPI_HOST}/search` |
| `TOOLS_SERVER_PORT` | Default `5005` — uvicorn port for `tools_server.py` |
| `HW07_MOCK_RAPIDAPI` | Mock flag (`1` = offline; not `USE_MOCK`) |
| `KAGGLE_USERNAME` / `KAGGLE_KEY` | Kaggle dataset download |

Run `python scripts\verify_env.py` — prints OK/MISSING only, never secret values.

---

## 6-step run guide

### 1. Environment

See **Quick setup** above.

### 2. Download dataset

```powershell
python data\download_dataset.py
```

Idempotent — skips if `data/job_postings.csv` exists. Source: [data-science-job-postings-and-skills](https://www.kaggle.com/datasets/asaniczka/data-science-job-postings-and-skills).

### 3. Start Docker stack

Open http://localhost:3000 — both containers should be **healthy** (Open WebUI **v0.10.1**).

**Embeddings:** Admin → Settings → Documents → set embedding model to `nomic-embed-text` (after `ollama pull nomic-embed-text`).

**Upgrading from 0.6.x:** if the container crash-loops after pull, reset legacy user settings (preserves KB/uploads):

```powershell
docker compose stop open-webui
docker run --rm -v hw07_open-webui-hw07:/data -v ${PWD}/scripts/fix_webui_db_migration.py:/fix.py:ro python:3.12-slim python /fix.py /data/webui.db
docker compose up -d open-webui
```

If that fails, remove the volume and recreate KB/tools (step 4–5 or `e2e/capture_screenshots.py`):

```powershell
docker compose down
docker volume rm hw07_open-webui-hw07
docker compose up -d
```

**Model settings:** Admin → Models → `llama3.2:3b` → Advanced → Function Calling = **Native**. Enable tool `hw07_live_job_search` in chat (+ icon).

### 4. Knowledge Base (no Python in KB path)

1. Workspace → **Knowledge** → Create → name `ai-job-postings`
2. Upload `data/job_postings.csv`
3. Wait until indexed (~12K rows; may take several minutes)
4. New chat → attach `#ai-job-postings` → ask demo KB questions below

### 5. Tool server + Web UI Tool

**Open WebUI:** Workspace → **Tools** → paste contents of [`openwebui_tool.py`](openwebui_tool.py) → Save.

Confirm Valves → `tools_server_url` = `http://host.docker.internal:5005` (not `localhost` — Open WebUI runs in Docker).

Chat prompt: *“Use search_live_jobs: what DevOps or AI engineer jobs are open in Israel right now?”*

### 6. Tests + screenshots

```powershell
# Terminal B — tool server required for E2E + Playwright tests:
.\scripts\start_tool_server.ps1 -MockRapidApi

python -m pytest tests\ -q -m "not live"
```
# Full submission workflow (setup + all 9 screenshots):
.\scripts\run_submission.ps1
# Or manually:
python e2e\capture_screenshots.py --setup-only --skip-warmup
python e2e\capture_screenshots.py --skip-warmup --kb-ready
```

Resume partial capture: `python e2e\capture_screenshots.py --no-clean --skip-warmup --from-step 3`

Step 3 fallback (API chat, faster on 3B): `python e2e\capture_kb_answer.py` then `--from-step 4`

---

## Demo questions

### Knowledge Base (attach `#ai-job-postings`)

| # | Prompt |
|---|--------|
| 1 | Based on the uploaded job postings CSV, what are the most common AI job titles? |
| 2 | Which skills appear most often in the job postings dataset? |
| 3 | What locations appear most often in the dataset? |
| 4 | Compare AI Engineer, Data Scientist, and Machine Learning Engineer roles based on the CSV. |
| 5 | Give me 5 insights from the uploaded job postings dataset. |

### Live tool (`search_live_jobs` / `hw07_live_job_search`)

| # | Prompt |
|---|--------|
| 1 | Search live AI Engineer jobs in Israel. |
| 2 | Search live Machine Learning Engineer jobs in Tel Aviv. |
| 3 | Search live Data Scientist jobs that support remote work. |
| 4 | Find junior AI Engineer jobs in Israel. |
| 5 | Search live DevOps AI automation jobs. |

### Hybrid (KB + tool)

| # | Prompt |
|---|--------|
| 1 | Based on the CSV, what skills should I learn, and then search live jobs in Israel for those skills. |
| 2 | Compare the uploaded job market data with live AI Engineer jobs in Israel. |
| 3 | Use the Knowledge Base for historical/static dataset insights and the live tool for current job listings. |

---

## Screenshot checklist

Submission evidence in `screenshots/`:

| File | Shows |
|------|--------|
| `00-signed-in.png` | Open WebUI signed in, `llama3.2:3b` model |
| `01-kb-upload.png` | Knowledge collection `ai-job-postings` + `job_postings.csv` (Kaggle) |
| `02-kb-indexed.png` | CSV indexed (~3.8 MB) |
| `03-kb-answer.png` | KB chat — user prompt + grounded answer (job titles, companies) |
| `04-tool-registered.png` | Workspace → Tools — `HW07 Live Job Search` |
| `05-tool-function-io.png` | Tool code — `search_live_jobs(role, location)` → `host.docker.internal:5005` |
| `06-model-system-prompt.png` | Model preset — Native FC, system prompt, tool attached |
| `07-live-tool-answer.png` | Tool chat — live or mock JSearch results |
| `08-docker-healthy.png` | `docker compose ps` — both containers healthy |

---

## Security notes

- `.env` is gitignored — only [`.env.example`](.env.example) with placeholders is committed.
- `RAPIDAPI_KEY` stays in local `.env` only; never log, print, or commit it.
- `scripts/verify_env.py` reports OK/MISSING without exposing secret values.
- `tools_server.py` returns structured JSON errors — no API keys in responses.
- Subscribe to [JSearch on RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) and use **that app's** key with `RAPIDAPI_HOST=jsearch.p.rapidapi.com`.

---

## Assignment mapping

| Requirement | Implementation |
|-------------|----------------|
| **1. KB (Web UI)** | Kaggle CSV → Workspace → Knowledge → `ai-job-postings` (no Python in KB path) |
| **2. Local Python server** | `tools_server.py` on `:5005` — `GET /health`, `POST /jobs/search` → JSearch (RapidAPI) |
| **3. Web UI Tool** | `openwebui_tool.py` → `search_live_jobs(role, location)` calls `host.docker.internal:5005` |
| **System prompt** | [`prompts/system_prompt.md`](prompts/system_prompt.md) — KB for historical CSV; tool for live hiring |
| **Model** | `llama3.2:3b` via Ollama — Function Calling = **Native**, tool `hw07_live_job_search` enabled |

---

## Layout

| Path | Role |
|------|------|
| `docker-compose.yml` | Ollama + Open WebUI |
| `tools_server.py` | FastAPI on `:5005` — `/health`, `/jobs/search` |
| `openwebui_tool.py` | Paste into Workspace → Tools |
| `prompts/system_prompt.md` | Model preset system prompt (auto-applied by E2E) |
| `jsearch_client.py` | JSearch RapidAPI client (mockable) |
| `scripts/reset_webui_password.py` | Normalize admin@localhost.com / admin for E2E API auth |
| `scripts/verify_env.py` | Env var presence check (no secret values) |
| `tests/test_tools_server.py` | pytest (mock mode + edge cases) |
| `e2e/capture_screenshots.py` | Playwright evidence |
| `screenshots/` | Submission PNGs |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tool not firing | Native function calling on `llama3.2:3b`; enable `hw07_live_job_search` in chat; use explicit “use search_live_jobs” in prompt |
| Tool server unreachable from UI | Use `host.docker.internal:5005`; `extra_hosts` in compose |
| Empty JSearch results | Try broader query; check RapidAPI quota |
| JSearch 404 / `Endpoint '/search' does not exist` | Subscribe to JSearch on RapidAPI; use that app's `RAPIDAPI_KEY` in `.env` |
| Port 3000 already in use | Stop other `open-webui` container: `docker stop open-webui`; then `docker compose up -d` in `homework/hw07` |
| API sign-in fails (400) | Run `python scripts/reset_webui_password.py` after stack is healthy; ensure `WEBUI_SECRET_KEY` is set in [`docker-compose.yml`](docker-compose.yml) |
| Slow KB index | ~12K rows; wait for FAISS completion; check indexing logs in Open WebUI |
| Screenshot automation timeout | Resume: `python e2e\capture_screenshots.py --no-clean --skip-warmup --from-step N` or capture manually per checklist above |
| `llama3.2:3b not found` | Run `docker exec hw07-ollama ollama pull llama3.2:3b` |
| Qwen3.6 in Open WebUI | Start host `llama-server` on `:8080` (`lectures/11_local_models_webui/scripts/start_llama_server.ps1`); Admin → Connections → OpenAI API → `http://host.docker.internal:8080/v1` (no key). Keep Ollama for embeddings + hw07 tools. |

---

## Manual fallback (if E2E automation fails)

1. Workspace → Knowledge → `ai-job-postings` → upload `data/job_postings.csv` → wait for index
2. Workspace → Tools → paste [`openwebui_tool.py`](openwebui_tool.py) → verify Valves URL = `http://host.docker.internal:5005`
3. Admin → Models → `llama3.2:3b` → Function Calling = Native → attach `hw07_live_job_search`
4. Run demo prompts above and capture screenshots per checklist
