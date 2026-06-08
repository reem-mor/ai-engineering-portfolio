# PITER Tools, MCP, and Lambda Live Check

**Date:** 2026-06-08

## Production tool path

Bedrock Action Groups backed by AWS Lambda are the production tool path. MCP is represented as a standardized tool-contract layer for local/demo and future integrations (`tests/test_mcp_server.py`).

## Four PITER tool responsibilities

| Tool | Lambda / local | Status |
|------|----------------|--------|
| piter-recent-deployments | Action group + local enricher | Verified |
| piter-service-context | Action group + local enricher | Verified |
| piter-similar-incidents | Action group + local enricher | Verified |
| piter-escalation | Lambda deployed; mock-safe default | Verified |

## Checks

- Input/output schema — OpenAPI GET query params for escalation
- No raw contacts in tool output — masked in UI
- Local tests — `tests/test_piter_lambdas.py`, `tests/test_mcp_server.py` — pass
- Agent selects tools — smoke scenarios pass with enrichment fields populated

## Known risk (code review)

`piter-escalation` Lambda zip includes only `lambda_function.py`. **Live** SNS/SES dispatch from Lambda requires bundling `app.services.notification_dispatch` — do not enable live gates until repackaged. Demo uses Flask `/api/escalation/notify` path.

## Prior reports

`PITER_LAMBDA_ACTION_GROUP_AWS_CHECK.md`, `PITER_ESCALATION_LAMBDA_DEPLOYMENT.md`
