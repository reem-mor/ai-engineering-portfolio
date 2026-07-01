# HW07 Submission — AI Job Market Intelligence Assistant

Open WebUI + Kaggle AI job-market knowledge base + live job-search tool server (RapidAPI JSearch).

## What was built

| Component | Description |
|-----------|-------------|
| **Knowledge Base** | **AI Job Market Intelligence Dataset** — Kaggle AI jobs CSV (`data/ai_jobs.csv`) indexed for static/RAG questions |
| **Tool server** | FastAPI at `http://localhost:5005` — `search_jobs`, `search_jobs_by_company`, `search_jobs_by_skill` (OpenAPI) |
| **Live upstream** | RapidAPI **JSearch** (`RAPIDAPI_JOBS_HOST`, key in repo root `.env`) |
| **Custom model** | `ai-job-market-assistant` on `llama3.1:latest` with KB + native function calling |
| **System prompt** | [`prompts/system_prompt.md`](prompts/system_prompt.md) — routes KB vs live tool, forbids invented data |

## How to run (reproduce)

```powershell
cd homework\hw07
docker compose up -d                      # hw07-open-webui + hw07-ollama + hw07-tool-server
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1

# Env: repo root .env — RAPIDAPI_KEY, RAPIDAPI_JOBS_HOST, KAGGLE_API_TOKEN,
#      OWUI_EMAIL + OWUI_PASSWORD (or OWUI_API_KEY)
python data\download_dataset.py           # Kaggle CSV → data/ai_jobs.csv
python data\validate_dataset.py           # topic/columns/rows validation
python scripts\bootstrap_owui.py          # KB + tool registration + custom model

python scripts\verify_tool_server.py
python -m pytest -q
python scripts\run_demo_chats.py          # writes TEST_RESULTS.md
python scripts\capture_screenshots.py     # writes screenshots/*.png
```

## Docker services

| Service | Container | Port |
|---------|-----------|------|
| Open WebUI | `hw07-open-webui` | 3000 |
| Ollama | `hw07-ollama` | 11434 |
| Tool server | `hw07-tool-server` | 5005 |

## Evidence

- `TEST_RESULTS.md` — generated demo Q&A + direct tool-server test matrix
- [`TEST_QUESTIONS.md`](TEST_QUESTIONS.md) — full expected-behavior matrix
- [`screenshots/`](screenshots/README.md) — submission captures (sanitized)

## Security

No secrets committed: `.env` gitignored, repo root `.env` is the single source,
tool server never echoes the RapidAPI key, screenshots sanitized.
