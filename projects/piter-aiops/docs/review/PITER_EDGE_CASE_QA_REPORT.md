# PITER Edge Case QA Report

**Date:** 2026-06-08

Automated coverage via pytest (271 tests). Selected edge cases:

| Scenario | Coverage |
|----------|----------|
| Missing incident description | Triage validators / API |
| Invalid service / environment | Enrichment fallbacks |
| AWS unavailable / bad KB ID | Local fallback — `verify_live_demo` Phase B |
| No citations | Grounded=false paths; UI example badge |
| Tool timeout / Lambda invalid input | Lambda tests + mock responses |
| Upload unsupported file | `test_upload_routes.py` |
| Upload too large | `test_upload_validators.py` |
| Duplicate notification | `test_notification_dispatch.py` + idempotency key fix |
| Live notify without confirmation | `test_escalation_api.py` |
| Follow-up without session | API error handling |
| Guardrail prompts | `test_guardrails.py` |
| MCP contract drift | `test_mcp_server.py` |
| SPA bootstrap / alert stream bounds | `test_spa_mode.py`, `verify_spa_demo.py` |
| Docker restart | Manual — container healthy after recreate |

## Manual gaps (acceptable for demo)

- Browser refresh mid-storm — client state resets; user restarts storm
- Full live SNS/SES send — intentionally not executed

## Result

No regressions; baseline maintained.
