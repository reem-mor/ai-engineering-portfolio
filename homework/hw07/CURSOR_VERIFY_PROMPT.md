# Cursor prompt — verify hw07 end-to-end

Paste the block below into Cursor's agent with this repo open on your machine
(Docker Desktop running, keys already in the repo root `.env`).

---

You are working in `homework/hw07/` of this repo. Read `AGENTS.md` and `README.md` there first.
Your job is to VERIFY the AI Job Market Intelligence Assistant works end-to-end and fix anything
broken. Work step by step; do not skip a gate if the previous one failed — fix it first.

Environment rules (hard requirements):
- All secrets come from the repo root `.env` only (`RAPIDAPI_KEY`, `RAPIDAPI_JOBS_HOST`,
  `KAGGLE_API_TOKEN`, `OWUI_EMAIL`, `OWUI_PASSWORD`). Never print, hardcode, or commit a secret.
- Never edit files outside `homework/hw07/` except the root `.env` (via scripts only).
- Do not delete Docker containers/volumes that are not `hw07-*`.
- Report results honestly — never claim a step passed when it failed.

Gate 0 — environment:
- `cd homework\hw07`, create/activate `.venv`, `pip install -r requirements.txt`.
- Run `python scripts\verify_env.py` — must exit 0. If a var is missing, STOP and ask me for it.

Gate 1 — stack up:
- `docker compose up -d` then `docker compose ps` — expect `hw07-open-webui` (:3000),
  `hw07-ollama` (:11434), `hw07-tool-server` (:5005) all running.
- `docker exec hw07-ollama ollama pull nomic-embed-text` and `ollama pull llama3.1`.
- If port 3000/5005 is taken by an unrelated container, tell me — do not kill it yourself.

Gate 2 — dataset:
- `python data\download_dataset.py` (downloads the Kaggle "Global AI Job Market & Salary
  Trends 2025" CSV to `data\ai_jobs.csv`). If Kaggle auth fails, STOP and show me the manual step
  the script prints — do NOT substitute other data.
- `python data\validate_dataset.py` — must print "Dataset validation passed".

Gate 3 — tool server + RapidAPI:
- `python scripts\verify_tool_server.py` — must end with "OK: tool server verified" AND
  `rapidapi_configured=True` with a 200 live search. If it returns 503/502, check
  `RAPIDAPI_KEY`/`RAPIDAPI_JOBS_HOST` in root `.env` and my JSearch subscription on rapidapi.com;
  report the exact HTTP status without printing the key.

Gate 4 — Open WebUI (KB, system prompt, tool, model):
- `python scripts\bootstrap_owui.py` — creates/reuses KB "AI Job Market Intelligence Dataset",
  uploads `ai_jobs.csv` (polls processing), registers the tool server (OpenAPI), and creates model
  `ai-job-market-assistant` on `llama3.1:latest` with the system prompt from
  `prompts\system_prompt.md` and native function calling.
- Verify in the API or UI: KB exists and contains `ai_jobs.csv` (indexed, not pending); the model
  shows the system prompt and the tool; note KB id and file id (safe to show — they are not secrets).
- If the tool-server URL is wrong for your setup, set `HW07_TOOL_URL` accordingly
  (`http://tool-server:5005/openapi.json` for the compose service).

Gate 5 — questions & answers:
- `python scripts\run_demo_chats.py` — runs the demo matrix (KB-only, tool-only, mixed, negative)
  and writes `TEST_RESULTS.md`. All direct tool tests must PASS; chat tests must PASS or you must
  explain each failure and fix what is fixable (KB not indexed, tool not attached, model missing).
- Also run `python -m pytest tests\ -q` (all must pass) and `python scripts\run_all_checks.py`
  (everything PASS — nothing should SKIP on this machine).

Gate 6 — screenshots:
- `pip install playwright && playwright install chromium` if needed, then
  `python scripts\capture_screenshots.py` — fills `screenshots\` per `screenshots\README.md`
  (home, KB page, indexed file, model+system prompt, tool config, health, KB answer, live answer,
  mixed answer, docker status). Open each image and confirm no secrets are visible.

Gate 7 — commit:
- `git status` — stage ONLY `homework/hw07/TEST_RESULTS.md` and `homework/hw07/screenshots/*.png`.
- Confirm `.env` is untracked, run a quick secret grep over the staged files, then commit:
  `docs(hw07): add local E2E test results and submission screenshots` and push to main.

Final report — give me a table: gate | status | evidence (file/output line), plus KB id,
model id, RapidAPI host used, and any manual step still open.

---
