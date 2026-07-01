---
name: hw07-open-webui
description: Use when working on homework hw07 — Open WebUI knowledge base, local JSearch tools server, RapidAPI, Docker stack, or Playwright submission screenshots for the job-postings CSV assignment.
---

# HW07 — Open WebUI + Local Tools Server

## When to use

- Editing `homework/hw07/` (FastAPI tool server, Open WebUI Tool class)
- Open WebUI KB upload, tool registration, or E2E screenshots
- Kaggle dataset download for job postings CSV

## Read first

1. [`homework/hw07/README.md`](../../homework/hw07/README.md) — 6-step run guide
2. [Open WebUI tool development](https://docs.openwebui.com/features/extensibility/plugin/tools/development/)
3. [Open WebUI Knowledge](https://docs.openwebui.com/features/workspace/knowledge/)

## Stack

| Service | Container | Port |
|---------|-----------|------|
| Open WebUI | `hw07-open-webui` (`v0.10.1`) | 3000 |
| Ollama | `hw07-ollama` | internal 11434 |
| Tool server | host `tools_server.py` | 5005 |

Open WebUI Tool (`openwebui_tool.py`) calls **`http://host.docker.internal:5005`** — not OpenAPI registration.

## Quick start (Windows)

```powershell
cd homework\hw07\scripts
.\start_stack.ps1
docker exec hw07-ollama ollama pull llama3.1
.\start_tool_server.ps1 -MockRapidApi   # or live with RAPIDAPI_KEY in .env
```

## Env

Copy from `.env.example` — never commit `.env`.

## Tests

```powershell
cd homework/hw07
python -m pytest tests/ -q
```

## Screenshots

```powershell
python e2e/capture_screenshots.py
```

Output: `homework/hw07/screenshots/`

## Guardrails

- Tool server URL from Docker: `host.docker.internal:5005`
- Native function calling on `llama3.1`
- CI job: `hw07-tools-server` in `.github/workflows/ci.yml`
