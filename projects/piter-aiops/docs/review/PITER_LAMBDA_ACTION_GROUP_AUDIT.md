# PITER AiOps — Lambda & Action Group Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## The four PITER tools (`action_groups/piter-*`)

| Lambda | Purpose | Handler | Schema | Backing logic |
| ------ | ------- | ------- | ------ | ------------- |
| `piter-recent-deployments` | recent deploys, correlation, rollback availability | `lambda_function.py` | `openapi_schema.yaml` | `enrichment_tools.correlate_deployments()` |
| `piter-service-context` | owner, on-call role, business impact, priority/regulatory | `lambda_function.py` | `openapi_schema.yaml` | `lookup_owner_and_escalation()` + `score_business_impact()` |
| `piter-similar-incidents` | historical match, root cause, prior resolution + MTTR | `lambda_function.py` | `openapi_schema.yaml` | `find_similar_incidents()` |
| `piter-escalation` | escalation preview, recipient resolution, SNS/SES mock/preview/live gate, idempotency, confirmation | `lambda_function.py` | `openapi_schema.yaml` | `services/notification_dispatch.py` |

## Per-Lambda checklist
| Check | recent-deploys | service-context | similar | escalation |
| ----- | -------------- | --------------- | ------- | ---------- |
| Single responsibility | ✓ | ✓ | ✓ | ✓ |
| Input validation (400 on missing) | ✓ | ✓ | ✓ | ✓ |
| Stable JSON output | ✓ | ✓ | ✓ | ✓ |
| Structured error responses | ✓ | ✓ | ✓ | ✓ |
| Safe logging (no secrets) | ✓ | ✓ | ✓ | ✓ |
| No hardcoded contacts | ✓ | ✓ | ✓ | ✓ (after Commit 2 redaction) |
| Mock mode by default | n/a (read-only) | n/a | n/a | ✓ `PITER_NOTIFICATION_MODE=mock` |
| Preview mode | n/a | n/a | n/a | ✓ masked recipients |
| Live blocked unless confirmed | n/a | n/a | n/a | ✓ token + allowlist + severity |
| Idempotency | n/a | n/a | n/a | ✓ `idempotency_key` set |
| Tests (valid + failure) | `test_enrichment_tools.py`, `test_piter_lambdas.py` | same | same | `test_notification_dispatch.py`, `test_escalation_*` |
| OpenAPI schema present | ✓ | ✓ | ✓ | ✓ |

## Legacy duplicates (kept by decision)
`action_groups/iiq-context`, `iiq-correlate`, `iiq-similar`, `incidentiq-ops` mirror the same logic
and correspond to **live AWS function names**. Retained and documented; listed in
`PITER_PROPOSED_DELETIONS.md` (no deletion). Per `docs/mcp.md`: "AWS deployments may still use legacy
`iiq-*` function names; local tests/docs use `piter-*`."

## Single source of truth
Business logic lives in `app/enrichment_tools.py`; each Lambda is a thin adapter so AWS and
local/MCP paths share identical behavior.

## Status: 4 relevant, validated, tested Lambdas. Live deployment NOT VERIFIED (no creds).
