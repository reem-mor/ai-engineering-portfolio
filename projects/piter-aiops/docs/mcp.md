# MCP and Lambda tools

PITER demonstrates **tool use** through Amazon Bedrock Action Groups backed by AWS Lambda.
This is not the same as a standalone MCP server.

## Final four tools (local source of truth)

| Tool | Purpose |
|---|---|
| `piter-recent-deployments` | Deploy correlation and rollback hints |
| `piter-service-context` | Ownership, impact, escalation path |
| `piter-similar-incidents` | Historical matches and MTTR |
| `piter-escalation` | Safe notification preview (mock by default) |

Each tool has `lambda_function.py` and `openapi_schema.yaml` under `action_groups/piter-*/`.

## AWS vs local naming

AWS deployments may still use legacy `iiq-*` function names. Local tests and docs use `piter-*`.
Do not rename deployed Lambdas without explicit approval.

## MCP story (honest)

- **Implemented:** Bedrock action groups with OpenAPI schemas — agents call tools during triage.
- **Mocked:** Notification dispatch; deterministic CSV-driven storm visuals.
- **Planned:** Optional standalone MCP server exposing the same four contracts for IDE integrations.

The React SPA and `/console` show tool enrichment from the triage card response, not fabricated latency numbers.
