# AGENTS.md — CVE Intelligence Assistant (Open WebUI + RAG + live tool)

Context for the Cursor agent working in `homework/hw07/`. Read before acting.

## Goal

Three-part Open WebUI build for course HW07:

1. **Knowledge Base** — Kaggle CVE CSV indexed as an OWUI knowledge base (static / historical).
2. **Tool server** — `tools_server.py`, local FastAPI calling a live CVE API.
3. **Web UI tool** — tool server registered in OWUI via OpenAPI for *live* CVE questions.

Graded contrast: **KB = historical dataset questions; tool = current-risk questions** about the same CVE.

## Build order

1. Use `kaggle` MCP (or `python data/download_dataset.py`) to get a CVE CSV → `./data/cve.csv`.
2. Fill `.env` from `.env.example` (ask user for keys; never invent them).
3. Create KB + upload CSV: prefer `openwebui` MCP; else run `owui_kb_setup.py`.
4. Run tool server: `uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload`.
   Verify `GET /health` and `GET /cve/CVE-2021-44228`.
5. Guide user to register OpenAPI tool in OWUI and attach KB to a tool-capable model.

## Rules / guardrails

- **Secrets only in `.env`.** Never hardcode keys; never commit `.env`.
- **`owui_kb_setup.py` is idempotent** — reuses existing KB by name.
- **Networking:** OWUI in Docker → tool server at `http://host.docker.internal:5005`, NOT `localhost`.
- **RAG tuning** is in `docker-compose.yml` env vars, not admin clicks.
- **Endpoint drift:** if OWUI REST 4xxs, check `http://localhost:3000/docs`.
- **No destructive OWUI ops** (delete KB/users/chats) without explicit confirmation.

## Demo

- KB:   "What CVEs in my dataset affected Apache Struts, and what were their CVSS scores?"
- Tool: "What is the current EPSS score and KEV status for CVE-2021-44228?"
