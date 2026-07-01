# AGENTS.md — AI Job Market Intelligence Assistant (hw07)

Context for coding agents working in `homework/hw07/`. Read before acting.

## Goal

Three-part Open WebUI build:

1. **Knowledge Base** — Kaggle AI job-market CSV (`data/ai_jobs.csv`) indexed as
   OWUI KB **"AI Job Market Intelligence Dataset"** (static dataset questions).
2. **Tool server** — `tools_server.py` on :5005, live job search via RapidAPI
   (JSearch) — `/jobs/search`, `/jobs/company`, `/jobs/skills`.
3. **Web UI tool** — `ai_job_market_live_search` (OpenAPI registration or
   `owui_tool_ai_jobs.py`) for *live* job-market questions.

Graded contrast: **KB = static Kaggle dataset; tool = current live postings.**

## Build order

1. `python data/download_dataset.py` → `data/ai_jobs.csv`, then
   `python data/validate_dataset.py` (must pass before upload).
2. Secrets in **repo root `.env` only** (`RAPIDAPI_KEY`, `RAPIDAPI_JOBS_HOST`,
   `KAGGLE_API_TOKEN`, `OWUI_EMAIL`/`OWUI_PASSWORD` or `OWUI_API_KEY`).
3. `python owui_kb_setup.py --write-env` — idempotent, polls indexing status.
4. `uvicorn tools_server:app --host 0.0.0.0 --port 5005` — verify `/health`
   and `/jobs/search?query=ai engineer&location=Israel`.
5. Register tool in OWUI, attach KB + system prompt to a tool-capable model.
6. `python scripts/run_all_checks.py` before claiming done.

## Rules / guardrails

- **Secrets only in the repo root `.env`.** Never hardcode, print, or commit keys.
- **Topic lock:** dataset must stay AI job-market — `validate_dataset.py`
  rejects CVE/NVD or unrelated data. No silent fallback datasets/APIs.
- **Networking:** OWUI in Docker reaches the host tool server at
  `http://host.docker.internal:5005`, NOT `localhost`.
- **Endpoint drift:** if OWUI REST 4xxs, check `http://localhost:3000/docs`.
- **No destructive OWUI/Docker ops** (delete KBs, unrelated containers —
  e.g. hindsight) without explicit confirmation.
- Tests must stay offline-safe (mocked HTTP) — CI has no live keys.

## Demo

- KB:    "What are the most common AI job titles in the Kaggle dataset?"
- Tool:  "Search live AI Engineer jobs in Israel."
- Mixed: "Compare the Kaggle dataset trends with live AI Engineer jobs in Israel."
