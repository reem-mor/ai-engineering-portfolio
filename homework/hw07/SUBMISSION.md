# Submission Notes — HW07

## What to include

- Screenshots from [`screenshots/`](screenshots/) (files `01` through `06`)
- GitHub repository link in the email body
- Brief note that Open WebUI ran in Docker with Ollama backend

## Screenshot checklist

| File | Verify |
|------|--------|
| [`01-kb-collection-created.png`](screenshots/01-kb-collection-created.png) | Knowledge collection created in Open WebUI |
| [`02-kb-csv-uploaded.png`](screenshots/02-kb-csv-uploaded.png) | `netflix_titles.csv` uploaded |
| [`03-kb-indexed.png`](screenshots/03-kb-indexed.png) | CSV file visible on collection / indexing complete |
| [`04-kb-chat-answer.png`](screenshots/04-kb-chat-answer.png) | Chat answers a dataset question using KB |
| [`05-tool-server-configured.png`](screenshots/05-tool-server-configured.png) | Tool server URL `http://host.docker.internal:5005` saved |
| [`06-tool-chat-answer.png`](screenshots/06-tool-chat-answer.png) | Chat invokes a live tool (`country_info`) |

## Manual validation steps

1. Tool server health: `curl http://localhost:5005/health` → `{"status":"ok",...}`
2. OpenAPI docs: http://localhost:5005/docs loads in browser
3. KB chat returns facts from CSV without calling external APIs
4. Tool chat shows tool invocation in Open WebUI UI

See [`TEST-RESULTS.md`](TEST-RESULTS.md) for pytest and Playwright run details.

## Regenerate screenshots

```powershell
cd homework\hw07\scripts
.\start-stack.ps1 -MockRapidApi
cd ..\e2e
npm install
npx playwright install chromium
npx playwright test submission-screenshots.spec.ts
```

## Best practice

- Do not commit `.env`, API keys, or Open WebUI sqlite volumes.
- Keep screenshot names numbered and descriptive.
- Use `HW07_MOCK_RAPIDAPI=1` only for local E2E; validate live RapidAPI separately before submission.
