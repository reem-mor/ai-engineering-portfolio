# HW07 Screenshots

Submission evidence for Open WebUI Knowledge Base + live tools. Prefer Playwright capture ([`e2e/submission-screenshots.spec.ts`](../e2e/submission-screenshots.spec.ts)).

## Before you submit

Run validation:

```bash
homework/hw07/scripts/validate-submission.sh
```

**Manually verify** screenshots `04` and `06` show **complete** assistant text (not grey skeleton loader bars).

| File | Must show |
|------|-----------|
| `04-kb-chat-answer.png` | **2676** TV Show, **6131** Movie |
| `06-tool-chat-answer.png` | `country_info` tool call + **Brasília** |

## Regenerate

**Linux / macOS:**

```bash
cd homework/hw07/scripts
./start-stack.sh --mock-rapidapi
cd ../e2e
npm install
npx playwright install chromium
npx playwright test submission-screenshots.spec.ts
```

**Windows:** see [`SUBMISSION.md`](../SUBMISSION.md).

For a clean tool-server screenshot (`05`), reset the Docker volume first:

```bash
docker compose -f homework/hw07/docker-compose.yml down -v
```

Prerequisites: Ollama (`llama3.2:3b`), Docker, tool server on `:5005`.

| File | Content |
|------|---------|
| `01-kb-collection-created.png` | Knowledge collection in Open WebUI |
| `02-kb-csv-uploaded.png` | CSV upload step |
| `03-kb-indexed.png` | CSV file on collection |
| `04-kb-chat-answer.png` | KB-grounded chat response |
| `05-tool-server-configured.png` | Tool server settings |
| `06-tool-chat-answer.png` | Live tool invocation in chat |

Do not commit secrets visible in screenshots (API keys, tokens).
