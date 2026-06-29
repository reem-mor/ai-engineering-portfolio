---
name: hw07-open-webui
description: This skill should be used when working on homework hw07, Open WebUI knowledge base, local Ollama tools server, RapidAPI integration, start-stack scripts, or Playwright submission screenshots for the Netflix CSV assignment.
version: 1.0.0
---

# HW07 — Open WebUI + Local Tools Server

## When to use

- Editing `homework/hw07/open-webui-tools/` (FastAPI tool server)
- Open WebUI KB upload, tool registration, or E2E screenshots
- Deciding **local vs cloud** for this assignment
- Debugging RapidAPI mock/live mode or Docker ↔ host networking

## Canonical docs (read first)

1. [`homework/hw07/README.md`](../../homework/hw07/README.md) — quick start, checklist
2. [`homework/hw07/ARCHITECTURE.md`](../../homework/hw07/ARCHITECTURE.md) — flows, local/cloud decision, security
3. [`homework/hw07/OPEN-WEBUI.md`](../../homework/hw07/OPEN-WEBUI.md) — manual UI runbook

## Architecture summary

| Component | Where | Port |
|-----------|-------|------|
| Ollama (local LLM) | Host | 11434 |
| Open WebUI | Docker `hw07-open-webui` | 3001 |
| Tool server | Host uvicorn | 5005 |
| RapidAPI | Cloud HTTPS | — |

Open WebUI registers tools via **OpenAPI** at `http://host.docker.internal:5005` (not MCP).

## Stack commands

**Linux/macOS:**

```bash
homework/hw07/scripts/start-stack.sh --mock-rapidapi
homework/hw07/scripts/stop-stack.sh
```

**Windows:**

```powershell
homework\hw07\scripts\start-stack.ps1 -MockRapidApi
homework\hw07\scripts\stop-stack.ps1
```

## Tool server env

| Variable | Purpose |
|----------|---------|
| `RAPIDAPI_KEY` | Live RapidAPI calls |
| `HW07_MOCK_RAPIDAPI=1` | Deterministic mock for E2E |
| `RAPIDAPI_COUNTRIES_HOST` | Default `restcountries.p.rapidapi.com` |

Copy from `open-webui-tools/.env.example` — never commit `.env`.

## Verification

```bash
cd homework/hw07/open-webui-tools
python -m pytest tests -q
curl -sf http://localhost:5005/health
```

Playwright (stack must be running):

```bash
cd homework/hw07/e2e
npm install && npx playwright test submission-screenshots.spec.ts
```

## Implementation rules

- Tool routes return HTTP 200 + `{ok, source, data, error}` — Open WebUI expects structured tool failures.
- Keep sync `def` handlers + sync httpx (threadpool) unless concurrency requirements change.
- Normalize RapidAPI payloads in `rapidapi_client.py` before returning to the model.
- E2E `waitForAssistantReply` must match **assistant message text only**, not user prompts; wait until streaming completes (no skeleton bars).
- Run `homework/hw07/scripts/validate-submission.sh` before submission.
- Do not commit API keys, `.hw07-tool-server.pid`, or Open WebUI volumes.

## Related

- Lecture 11: [`lectures/11_local_models_webui/`](../../lectures/11_local_models_webui/)
- MCP contrast (Lecture 08): [`lectures/08_mcp/`](../../lectures/08_mcp/)
- CI job: `hw07-open-webui-tools` in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
