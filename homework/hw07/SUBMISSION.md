# Submission Notes — HW07

## GitHub solution path

| Item | URL |
|------|-----|
| **Repository** | https://github.com/reem-mor/amdocs-ai-course |
| **Homework folder** | https://github.com/reem-mor/amdocs-ai-course/tree/main/homework/hw07 |
| **Tool server** | https://github.com/reem-mor/amdocs-ai-course/tree/main/homework/hw07/open-webui-tools |
| **Architecture** | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| **Screenshots** | [`screenshots/`](screenshots/) (`01`–`06`) |

Include the **homework folder link** in your submission email body.

## What to include in the email

1. **Subject:** `HW07 — [Your Name] — Open WebUI KB + Live Tools`
2. **GitHub link:** `https://github.com/reem-mor/amdocs-ai-course/tree/main/homework/hw07`
3. **Brief note:** Open WebUI ran in Docker (`hw07-open-webui`) with Ollama backend (`llama3.2:3b`); tool server on host port 5005.
4. **Screenshots:** Attach `01` through `06` (or confirm they are committed under `homework/hw07/screenshots/`).

## Screenshot checklist

| File | Verify before submit |
|------|----------------------|
| [`01-kb-collection-created.png`](screenshots/01-kb-collection-created.png) | Collection `netflix-shows` created |
| [`02-kb-csv-uploaded.png`](screenshots/02-kb-csv-uploaded.png) | `netflix_titles.csv` uploaded |
| [`03-kb-indexed.png`](screenshots/03-kb-indexed.png) | CSV visible / indexing complete |
| [`04-kb-chat-answer.png`](screenshots/04-kb-chat-answer.png) | **Complete answer** citing **2676 TV Show** and **6131 Movie** (not skeleton loader bars) |
| [`05-tool-server-configured.png`](screenshots/05-tool-server-configured.png) | Tool server `http://host.docker.internal:5005` saved (one entry) |
| [`06-tool-chat-answer.png`](screenshots/06-tool-chat-answer.png) | **Tool call visible** (`country_info`) + answer **Brasília** (not skeleton bars) |

> **Important:** Screenshots `04` and `06` must show **finished** assistant responses. If you see grey placeholder bars, regenerate with the Playwright flow below.

## Pre-submit validation

```bash
homework/hw07/scripts/validate-submission.sh
```

Expected: **17 pytest passed**, all six PNG files present, manual review notes for 04/06.

## Manual validation steps

1. `curl http://localhost:5005/health` → `{"status":"ok","tools_ready":"true",...}`
2. OpenAPI docs: http://localhost:5005/docs
3. KB chat (`#netflix-shows`) returns CSV-grounded counts without external APIs
4. Tool chat shows **tool invocation UI** for `country_info`

## Regenerate screenshots

**Linux / macOS:**

```bash
cd homework/hw07/scripts
./start-stack.sh --mock-rapidapi
cd ../e2e
npm install
npx playwright install chromium
npx playwright test submission-screenshots.spec.ts
./../scripts/stop-stack.sh
```

**Windows (PowerShell):**

```powershell
cd homework\hw07\scripts
.\start-stack.ps1 -MockRapidApi
cd ..\e2e
npm install
npx playwright install chromium
npx playwright test submission-screenshots.spec.ts
.\stop-stack.ps1
```

### Fresh Open WebUI (avoid duplicate tool servers in screenshot 05)

```bash
docker compose -f homework/hw07/docker-compose.yml down -v
./homework/hw07/scripts/start-stack.sh --mock-rapidapi
```

Prerequisites: Ollama with `llama3.2:3b`, Docker, tool server on `:5005`.

## Live RapidAPI (optional, recommended before final submit)

For screenshot `06` with real API data (not mock):

```bash
# In open-webui-tools/.env
RAPIDAPI_KEY=your_key
HW07_MOCK_RAPIDAPI=0
```

```bash
curl -X POST http://localhost:5005/tools/country_info \
  -H "Content-Type: application/json" \
  -d '{"country_name":"Brazil"}'
```

Expect `ok=true`, `"source":"rapidapi"`, and live country payload.

## Best practice

- Do not commit `.env`, API keys, or Open WebUI sqlite volumes.
- Use `HW07_MOCK_RAPIDAPI=1` for E2E capture; validate live RapidAPI separately.
- See [`TEST-RESULTS.md`](TEST-RESULTS.md) for pytest and Playwright run details.
