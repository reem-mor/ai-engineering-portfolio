# PITER Test & QA Report

**Date:** 2026-06-08

## Automated runs (this session)

| Suite | Result |
|-------|--------|
| `py -3.12 -m pytest` | **251 tests — ALL PASSED** |
| `py -3.12 scripts/verify_live_demo.py` | **29/29 PASS** |
| `py -3.12 scripts/kb_smoke_test.py` | 7/7 (prior session) |
| `py -3.12 scripts/agent_smoke_test.py` | 7/7 (prior session) |
| Frontend `npm ci && npm run build` | **NOT RUN** this session |
| Docker health | **NOT VERIFIED** — daemon stopped |

## Test categories coverage

| Category | Tests |
|----------|-------|
| Health / routes | `test_flask_routes.py`, `test_spa_mode.py` |
| Dataset validation | `test_source_data.py` |
| Incident analysis | `test_incident_analysis.py` (new) |
| Enrichment tools | `test_enrichment_tools.py` |
| Lambdas | `test_piter_lambdas.py`, `test_lambda_action_handler.py` |
| Guardrails | `test_guardrails.py` |
| Upload | `test_upload_service.py` |
| Bedrock clients | `test_bedrock_client.py`, `test_bedrock_agent_client.py` |
| Memory / follow-up | `test_agent.py` |
| Notifications | `test_notification_dispatch.py` (if present) |

## Gaps

1. Follow-up after P1 storm triage
2. RB-012–014 through `analyze_incident`
3. Upload → local RAG visibility
4. E2E Playwright against Docker (scripts exist — not run)

## verify_live_demo phases

- **Phase A:** Live Bedrock (`USE_BEDROCK=true`) — citations, tools, memory
- **Phase B:** Bad KB id → local fallback — same checks

## Recommendation before recording

1. Start Docker Desktop
2. `docker compose up -d && curl /health`
3. `npm run build` in frontend if UI changed
4. Re-run verify script
