# PITER Final Live E2E Validation

**Date:** 2026-06-08

## Automated gates

| Command | Result |
|---------|--------|
| `python -m pytest` | **271 passed** |
| `python scripts/verify_live_demo.py` | **29/29** |
| `python scripts/verify_spa_demo.py` | **36/36** |
| `RAG_BACKEND=agent python scripts/agent_smoke_test.py` | **7/7** |

## Docker

```powershell
docker compose ps          # piter-aiops Up (healthy)
curl http://localhost:8080/health   # 200
```

## Manual / browser

- SPA `/` — dashboard, storm, triage, tools, memory, KB, settings
- Legacy `/console` — bedrock triage + follow-up memory
- Screenshots captured — see `PITER_SCREENSHOT_CAPTURE_REPORT.md`

## Frontend build

```powershell
cd frontend
npm ci
npm run build
docker compose up -d --build
```

## Acceptance

All FINAL ACCEPTANCE CRITERIA from live demo mission met except optional live SNS/SES send (intentionally skipped).
