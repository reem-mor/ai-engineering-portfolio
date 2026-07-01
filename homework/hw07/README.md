# HW07 — AI Job Market Intelligence Assistant

Self-hosted Open WebUI assistant that answers **static** questions from a Kaggle
AI job-market dataset (RAG knowledge base) and **live** job-market questions
through a local tool server backed by a RapidAPI job-search provider.

## Architecture

```
User ── Open WebUI ── Knowledge Base (Kaggle ai_jobs.csv)          → dataset questions
             │
             └─ Tool: ai_job_market_live_search
                      → tools_server.py (localhost:5005)
                      → RapidAPI JSearch                            → live job questions
```

## Dataset — why this one

**[Global AI Job Market & Salary Trends 2025](https://www.kaggle.com/datasets/bismasajjad/global-ai-job-market-and-salary-trends-2025)**
(`bismasajjad/global-ai-job-market-and-salary-trends-2025`) — a single clean CSV
(~15k rows) with exactly the columns an assistant needs: `job_title`,
`salary_usd`, `experience_level`, `company_location`, `company_name`,
`required_skills`, `industry`, `remote_ratio`, `posting_date`. One file, no
joins, ideal for KB chunking and aggregate questions.

## RapidAPI provider — why JSearch

**JSearch** (`jsearch.p.rapidapi.com`) — the most reliable free-tier job-search
API on RapidAPI; aggregates Google for Jobs (LinkedIn/Indeed/Glassdoor
postings), supports role + location queries, returns structured salary/remote
fields matching the dataset topic. Host is configurable via
`RAPIDAPI_JOBS_HOST`, so Active Jobs DB or another provider can be swapped in
without code changes to the key handling.

## Layout

| File | Purpose |
|------|---------|
| [`tools_server.py`](tools_server.py) | FastAPI on :5005 — `/health`, `/jobs/search`, `/jobs/company`, `/jobs/skills` |
| [`owui_kb_setup.py`](owui_kb_setup.py) | Idempotent KB create/upload/attach + processing polling + `--write-env` |
| [`owui_tool_ai_jobs.py`](owui_tool_ai_jobs.py) | Open WebUI tool `ai_job_market_live_search` (paste into Workspace > Tools) |
| [`env_loader.py`](env_loader.py) | Shared env loading — repo root `.env` first, hw07 `.env` fills gaps |
| [`data/download_dataset.py`](data/download_dataset.py) | Kaggle download → `data/ai_jobs.csv` |
| [`data/validate_dataset.py`](data/validate_dataset.py) | Validates rows/columns/topic before upload |
| [`prompts/system_prompt.md`](prompts/system_prompt.md) | Model system prompt (raw text, loaded by bootstrap) |
| [`scripts/bootstrap_owui.py`](scripts/bootstrap_owui.py) | One-shot OWUI setup: KB + tool-server registration + custom model |
| [`scripts/verify_tool_server.py`](scripts/verify_tool_server.py) | Health + live/negative endpoint verification |
| [`scripts/run_demo_chats.py`](scripts/run_demo_chats.py) | Runs demo Q&A via OWUI API, writes `TEST_RESULTS.md` |
| [`scripts/capture_screenshots.py`](scripts/capture_screenshots.py) | Playwright submission screenshots |
| [`scripts/run_all_checks.py`](scripts/run_all_checks.py) | One-shot validation (syntax, dataset, pytest, health, live, KB, secret scan) |
| [`TEST_QUESTIONS.md`](TEST_QUESTIONS.md) | Demo/test matrix with expected behaviors |
| [`SUBMISSION.md`](SUBMISSION.md) | Submission summary + reproduce steps |
| [`docker-compose.yml`](docker-compose.yml) | hw07-open-webui + hw07-ollama + hw07-tool-server |
| [`screenshots/`](screenshots/README.md) | Required submission screenshots |

## Environment (root `.env` is canonical)

All scripts load the **repo root `.env` first** ([template](../../.env.example)),
then optional non-secret defaults from `homework/hw07/.env`. Never commit either.

| Variable | Purpose |
|----------|---------|
| `RAPIDAPI_KEY` | RapidAPI key (required for live search) |
| `RAPIDAPI_JOBS_HOST` | Provider host — default `jsearch.p.rapidapi.com` |
| `RAPIDAPI_JOBS_BASE_URL` | Optional; defaults to `https://<host>` |
| `KAGGLE_API_TOKEN` | Kaggle dataset download |
| `OWUI_URL` | Open WebUI base — `http://localhost:3000` |
| `OWUI_API_KEY` *or* `OWUI_EMAIL`+`OWUI_PASSWORD` | KB setup auth |
| `OWUI_KNOWLEDGE_ID`, `OWUI_FILE_ID` | Written by `owui_kb_setup.py --write-env` |

## Quickstart (Windows, from `homework\hw07`)

```powershell
# 1. Stack (Open WebUI :3000 + Ollama + tool server :5005)
docker compose up -d
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1

# 2. Python deps
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Dataset (KAGGLE_API_TOKEN in repo root .env)
python data\download_dataset.py
python data\validate_dataset.py

# 4. One-shot OWUI setup: KB + tool registration + custom model
python scripts\bootstrap_owui.py

# 5. Verify
python scripts\verify_tool_server.py
curl "http://localhost:5005/jobs/search?query=ai%20engineer&location=Israel"
```

The tool server runs as compose service `hw07-tool-server`
([`Dockerfile.tool-server`](Dockerfile.tool-server)); to run it on the host
instead use `uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload`
and set `HW07_TOOL_URL=http://host.docker.internal:5005/openapi.json`.

## Open WebUI wiring

`scripts/bootstrap_owui.py` does all of this via the REST API (KB upload,
tool-server registration at `http://tool-server:5005/openapi.json`, custom
model `ai-job-market-assistant` with the system prompt + native function
calling). Manual alternative:

1. **Tool** — either:
   - *OpenAPI (preferred):* Admin > Settings > External Tools > add
     `http://tool-server:5005/openapi.json` (or
     `http://host.docker.internal:5005/openapi.json` for a host-run server), or
   - *Workspace tool:* Workspace > Tools > create `ai_job_market_live_search`,
     paste [`owui_tool_ai_jobs.py`](owui_tool_ai_jobs.py).
2. **Model** — Workspace > Models > pick a tool-capable model (`llama3.1`):
   attach the **AI Job Market Intelligence Dataset** KB, enable the tool,
   enable native function calling, paste the [system prompt](prompts/system_prompt.md).

## Tests & validation

```powershell
python -m pytest tests/ -q          # offline unit tests (mocked HTTP)
python scripts\verify_env.py        # env vars present (no values printed)
python scripts\run_all_checks.py    # full PASS/FAIL/SKIP matrix
```

CI runs the pytest suite offline (`hw07-tools-server` job) — no live keys needed.

## Demo questions

See [`TEST_QUESTIONS.md`](TEST_QUESTIONS.md) for the full matrix. Quick set:

- **KB:** "What are the most common AI job titles in the Kaggle dataset?"
- **Tool:** "Search live AI Engineer jobs in Israel."
- **Mixed:** "Compare the Kaggle dataset trends with live AI Engineer jobs in Israel."

## Screenshots

Required captures listed in [`screenshots/README.md`](screenshots/README.md) —
sanitize before saving (no keys, tokens, or credentials visible).

## Security notes

- **No secrets committed** — `.env` files are gitignored; only sanitized
  `.env.example` templates are tracked.
- **Root `.env` only** — scripts never require secrets in `homework/hw07/.env`.
- The tool server and tool return errors **without echoing keys**; the RapidAPI
  key never leaves `tools_server.py`.
- Screenshots must be sanitized before commit.
