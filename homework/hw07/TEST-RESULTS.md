# HW07 Test Results (2026-06-28)

Stack: Open WebUI `0.6.15` (Docker `:3001`), Ollama `llama3.2:3b`, tool server `:5005` with `HW07_MOCK_RAPIDAPI=1` for deterministic tool responses during Playwright capture.

## pytest (`open-webui-tools/tests/`)

```text
13 passed
```

Coverage highlights:

- Health + mock-mode observability
- OpenAPI contract (3 tool POST operations, readable summaries)
- RapidAPI client fakeable seam (`httpx.MockTransport`, monkeypatched methods)
- Structured error responses when `RAPIDAPI_KEY` is missing

## API smoke

| Check | Result |
|-------|--------|
| `GET /health` | `{"status":"ok","mock_mode":"true",...}` |
| `POST /tools/country_info` (mock) | `ok=true`, `capital=Brasília` |
| `GET /openapi.json` | `search_title`, `country_info`, `streaming_status` |

## Playwright E2E

Command:

```powershell
cd homework\hw07\scripts
.\start-stack.ps1 -MockRapidApi
cd ..\e2e
npm install
npx playwright install chromium
npx playwright test submission-screenshots.spec.ts
```

| Step | Prompt / action | Result |
|------|-----------------|--------|
| KB upload | Create `netflix-shows`, upload CSV | PASS |
| KB chat | "How many rows are type TV Show vs Movie…" | PASS — answer references dataset types |
| Tool register | `http://host.docker.internal:5005` | PASS — Connections saved |
| Tool chat | "What is the capital of Brazil?" | PASS — `country_info` mock/live response |

## Screenshots

| File | Source |
|------|--------|
| [01-kb-collection-created.png](screenshots/01-kb-collection-created.png) | Playwright — Knowledge create |
| [02-kb-csv-uploaded.png](screenshots/02-kb-csv-uploaded.png) | Playwright — CSV upload |
| [03-kb-indexed.png](screenshots/03-kb-indexed.png) | Playwright — file on collection |
| [04-kb-chat-answer.png](screenshots/04-kb-chat-answer.png) | Playwright — KB chat |
| [05-tool-server-configured.png](screenshots/05-tool-server-configured.png) | Playwright — Admin → Tools |
| [06-tool-chat-answer.png](screenshots/06-tool-chat-answer.png) | Playwright — live tool chat |

## Live RapidAPI validation (optional)

With `RAPIDAPI_KEY` set and `HW07_MOCK_RAPIDAPI=0`:

```powershell
curl -X POST http://localhost:5005/tools/country_info `
  -H "Content-Type: application/json" `
  -d '{"country_name":"Brazil"}'
```

Expect `ok=true` and live country payload from RapidAPI.
