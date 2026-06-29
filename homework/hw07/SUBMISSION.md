# Submission — HW07

**GitHub solution:** https://github.com/reem-mor/amdocs-ai-course/tree/main/homework/hw07

Interactive setup guide: [`README.md`](README.md)

## Email template

**Subject:** `HW07 — [Your Name] — Open WebUI KB + Live Tools`

**Body:**

```
GitHub: https://github.com/reem-mor/amdocs-ai-course/tree/main/homework/hw07

Stack: Open WebUI (Docker :3001) + Ollama llama3.2:3b + FastAPI tool server (:5005)
Dataset: netflix_titles.csv indexed as #netflix-shows
Tools: country_info, search_title, streaming_status via RapidAPI

Screenshots 01–06 attached (or committed under homework/hw07/screenshots/).
```

## Screenshot checklist

| # | File | Must show |
|---|------|-----------|
| 01 | `01-kb-collection-created.png` | Collection `netflix-shows` |
| 02 | `02-kb-csv-uploaded.png` | CSV uploaded |
| 03 | `03-kb-indexed.png` | Indexing complete |
| 04 | `04-kb-chat-answer.png` | **2676** TV Show / **6131** Movie — full answer |
| 05 | `05-tool-server-configured.png` | One tool server at `host.docker.internal:5005` |
| 06 | `06-tool-chat-answer.png` | `country_info` tool call + **Brasília** |

## Pre-submit

```bash
homework/hw07/scripts/validate-submission.sh
cd homework/hw07/open-webui-tools && python -m pytest tests -q
```

## Regenerate screenshots

See [`README.md`](README.md#regenerate-all-screenshots-playwright).

Fresh Docker volume before capture:

```bash
docker compose -f homework/hw07/docker-compose.yml down -v
homework/hw07/scripts/start-stack.sh --mock-rapidapi
cd homework/hw07/e2e && npm install && npx playwright test submission-screenshots.spec.ts
```

## Do not commit

`.env`, API keys, Open WebUI sqlite volumes, `.hw07-tool-server.pid`
