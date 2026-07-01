---
name: hw07-open-webui
description: Use when working on homework hw07 — Open WebUI CVE knowledge base, local FastAPI tools server, RapidAPI/Shodan CVEDB, Docker stack, or Kaggle dataset download.
---

# HW07 — Open WebUI + CVE Tool Server

## When to use

- Editing `homework/hw07/` (FastAPI tool server, KB setup script)
- Open WebUI KB upload, OpenAPI tool registration
- Kaggle CVE dataset download

## Read first

1. [`homework/hw07/README.md`](../../homework/hw07/README.md) — quickstart
2. [Open WebUI Knowledge](https://docs.openwebui.com/features/workspace/knowledge/)
3. [Open WebUI external tools](https://docs.openwebui.com/features/extensibility/plugin/tools/)

## Stack

| Service | Container | Port |
|---------|-----------|------|
| Open WebUI | `hw07-open-webui` | 3000 |
| Ollama | `hw07-ollama` | internal 11434 |
| Tool server | host `tools_server.py` | 5005 |

Open WebUI registers the tool via **OpenAPI** at `http://host.docker.internal:5005/openapi.json`.

## Quick start (Windows)

```powershell
cd homework\hw07\scripts
.\start_stack.ps1
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1
python ..\data\download_dataset.py
.\start_tool_server.ps1
```

## Env

Copy from `homework/hw07/.env.example` — never commit `.env`.
Repo root `.env` may hold `KAGGLE_API_TOKEN`, `RAPIDAPI_KEY`, `OWUI_API_KEY`.

## Tests

```powershell
cd homework/hw07
python -m pytest tests/ -q
```

## MCP

Root `.mcp.json` includes `kaggle`. Optional `openwebui` block in [`homework/hw07/mcp.json.example`](../../homework/hw07/mcp.json.example) → copy to gitignored `.cursor/mcp.json`.

## Guardrails

- Tool server URL from Docker: `host.docker.internal:5005`
- Native function calling on `llama3.1`
- RapidAPI optional — Shodan CVEDB fallback when unset
- CI job: `hw07-tools-server` in `.github/workflows/ci.yml`
