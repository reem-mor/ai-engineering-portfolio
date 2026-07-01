---
name: hw07-open-webui
description: Use when working on homework hw07 — Open WebUI AI job-market knowledge base, local FastAPI tools server, RapidAPI JSearch live job search, Docker stack, or Kaggle dataset download.
---

# HW07 — Open WebUI + AI Job Market Tool Server

## When to use

- Editing `homework/hw07/` (FastAPI tool server, KB setup script)
- Open WebUI KB upload, tool registration (`ai_job_market_live_search`)
- Kaggle AI job-market dataset download / validation

## Read first

1. [`homework/hw07/README.md`](../../homework/hw07/README.md) — quickstart + architecture
2. [`homework/hw07/AGENTS.md`](../../homework/hw07/AGENTS.md) — build order + guardrails
3. [Open WebUI Knowledge](https://docs.openwebui.com/features/workspace/knowledge/)
4. [Open WebUI external tools](https://docs.openwebui.com/features/extensibility/plugin/tools/)

## Stack

| Service | Container | Port |
|---------|-----------|------|
| Open WebUI | `hw07-open-webui` | 3000 |
| Ollama | `hw07-ollama` | internal 11434 |
| Tool server | host `tools_server.py` (or `hw07-tool-server`, `--profile tools`) | 5005 |

Open WebUI registers the tool via **OpenAPI** at `http://host.docker.internal:5005/openapi.json`
(or paste `owui_tool_ai_jobs.py` as a Workspace tool).

## Quick start (Windows)

```powershell
cd homework\hw07\scripts
.\start_stack.ps1
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1
python ..\data\download_dataset.py
python ..\data\validate_dataset.py
python ..\owui_kb_setup.py --write-env
.\start_tool_server.ps1
```

## Env

Canonical secrets file: **repo root `.env`** — `RAPIDAPI_KEY`, `RAPIDAPI_JOBS_HOST`,
`KAGGLE_API_TOKEN`, `OWUI_EMAIL`/`OWUI_PASSWORD` (or `OWUI_API_KEY`).
`homework/hw07/.env` holds optional non-secret defaults only. Never commit `.env`.

## Tests

```powershell
cd homework/hw07
python -m pytest tests/ -q
python scripts\run_all_checks.py
```

## Guardrails

- Tool server URL from Docker: `host.docker.internal:5005`
- Native function calling on `llama3.1`
- Dataset topic is locked to AI job market — `data/validate_dataset.py` must pass before KB upload
- RapidAPI provider: JSearch (`jsearch.p.rapidapi.com`); host configurable via `RAPIDAPI_JOBS_HOST`
- CI job: `hw07-tools-server` in `.github/workflows/ci.yml` (offline, mocked HTTP)
