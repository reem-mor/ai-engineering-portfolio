# hw07 submission screenshots

Capture these on the machine running the hw07 stack (Playwright MCP or manual).
**Sanitize before saving: no API keys, tokens, emails/passwords, or `.env` contents visible.**

| # | File name | What it must show |
|---|-----------|-------------------|
| 01 | `01-open-webui-home.png` | Open WebUI running at `localhost:3000` |
| 02 | `02-kb-page.png` | Knowledge page showing **AI Job Market Intelligence Dataset** |
| 03 | `03-kb-file-indexed.png` | `ai_jobs.csv` attached and indexed in the KB |
| 04 | `04-model-system-prompt.png` | Model config with the system prompt from `prompts/system_prompt.md` |
| 05 | `05-tool-config.png` | Tool/function page showing `ai_job_market_live_search` (or the OpenAPI external tool) |
| 06 | `06-tool-server-health.png` | `http://localhost:5005/health` JSON response |
| 07 | `07-kb-question.png` | Successful KB-only Q&A (e.g. most common job titles in dataset) |
| 08 | `08-live-tool-question.png` | Successful RapidAPI live job-search answer |
| 09 | `09-mixed-question.png` | Successful mixed KB + tool answer |
| 10 | `10-terminal-tests.png` | `pytest` + `scripts/run_all_checks.py` results |
| 11 | `11-docker-status.png` | `docker ps` showing hw07-open-webui / hw07-ollama (/ hw07-tool-server) |
