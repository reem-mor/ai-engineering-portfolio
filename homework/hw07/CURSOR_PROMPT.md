# Master Cursor prompt

Paste the block below into Cursor's agent with this repo open.
Ensure `.cursor/mcp.json` has `kaggle` (from root `.mcp.json`) and optional `openwebui`
(from [`mcp.json.example`](mcp.json.example)) configured with env vars — not hardcoded keys.

---

You are working in `homework/hw07/`. Read `AGENTS.md` first and follow its build order.

Do the following end to end, pausing only to ask me for secrets you don't have:

1. Use the `kaggle` MCP to find a CVE / CVSS dataset. Show me 2–3 candidates with row
   counts and columns, let me pick one, then download its CSV into `./data/cve.csv`.
   If large, trim to a focused subset (keep header + human-readable summary column).

2. Copy `.env.example` to `.env` and ask me for: `OWUI_API_KEY` (Open WebUI > Settings >
   Account > API Keys), and optionally `RAPIDAPI_KEY` + `RAPIDAPI_HOST`. If I skip RapidAPI,
   leave those blank — the tool server falls back to Shodan CVEDB.

3. Create the knowledge base and upload the CSV. Prefer the `openwebui` MCP; if missing, run:
   `python owui_kb_setup.py --csv ./data/cve.csv --name "CVE Intelligence" --description "Historical CVE / CVSS records for RAG"`
   Print the resulting KB id.

4. Create a venv, `pip install -r requirements.txt`, start the tool server:
   `uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload`.
   Verify `GET http://localhost:5005/health` and `GET http://localhost:5005/cve/CVE-2021-44228`.

5. Give exact steps to (a) register OpenAPI tool at
   `http://host.docker.internal:5005/openapi.json`, (b) attach "CVE Intelligence" KB to
   `llama3.1`, and (c) run the two demo questions from AGENTS.md.

Constraints: never hardcode or commit secrets; keep `owui_kb_setup.py` re-runnable; if OWUI REST
4xxs, check `http://localhost:3000/docs`. Do not delete OWUI resources without asking.
