# Testing — Incident RAG Bedrock

All unit tests run **offline** with mocked Bedrock (no AWS credentials required).

## Quick run

```powershell
cd C:\dev\amdocs-ai-course\projects\incident-rag-bedrock
py -3.12 -m compileall .
py -3.12 -m pytest -q
```

## Frontend build (SPA served by Flask)

```powershell
cd frontend
npm ci
npm run build
# Output: ../app/static/spa/
```

## Docker smoke test

```powershell
cd C:\dev\amdocs-ai-course\projects\incident-rag-bedrock
docker compose up --build -d
Invoke-WebRequest http://localhost:8080/health
# Browser: http://localhost:8080/#live-kb and /#mvp (5 alerts, structured answers)
docker compose down
```

## Live Bedrock (optional)

Requires a valid `.env` with `BEDROCK_KB_ID` and an enabled inference profile in `BEDROCK_MODEL_ARN`:

```powershell
py -3.12 scripts/kb_smoke_test.py
```

After adding corpus files under `data/sample_documents/`, re-upload to S3 and **Sync** the Bedrock data source before running smoke tests.

## What is covered

| Area | Tests |
|------|--------|
| Answer sections + citation previews | `tests/test_text_utils.py` |
| Severity-based demo impact | `tests/test_workflow_impact.py` |
| 5 workflow alerts + demo questions | `tests/test_data_corpus.py` |
| JSON API shape (`answer_sections`, citations) | `tests/test_api_routes.py`, `tests/test_bedrock_client.py` |
| Legacy HTMX + SPA routes | `tests/test_routes.py`, `tests/test_spa_mode.py` |

## Unverified without AWS

- Bedrock KB sync status
- Live Q&A grounding against synced corpus
- EC2 public URL and IAM instance profile

Check in AWS Console: Knowledge Bases → data source **Available**, model access enabled, EC2 terminated when demo is done.
