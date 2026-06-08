# PITER Escalation Action Group Setup

**Date:** 2026-06-08  
**Agent:** `HH4YGSLZUE`  
**Action group:** `piter-escalation` (ID `SSK1JHTMJ4`)  
**Live alias version:** **6**

## Wiring

| Component | Value |
|-----------|--------|
| Executor | Lambda `piter-escalation` |
| OpenAPI S3 | `s3://reem-amdocs-ai-artifacts-3331/agent/piter-escalation/openapi_schema.yaml` |
| Lambda permission | `bedrock-agent-piter-escalation` (Bedrock principal) |
| Agent IAM | `incidentiq-agent-role` includes `lambda:InvokeFunction` on `piter-escalation` |

## OpenAPI fix

Initial POST body schema failed Bedrock validation. Schema rewritten to **GET** with query parameters (aligned with `iiq-*` groups). Lambda default HTTP method updated to `GET`.

## Agent versions

| Version | `piter-escalation` | Notes |
|---------|-------------------|--------|
| 3 | Absent | Pre-mutation live |
| 4 | Present | Guardrail v2 attached |
| 6 | Present, ENABLED | `incidentiq-ops` DISABLED |

## Smoke validation

With `RAG_BACKEND=agent`:

- `scripts/agent_smoke_test.py`: **7/7 PASS** on alias v6
- P1 bet-service prompt: grounded response with citations; escalation stays mock/preview
- No raw phone/email in agent output; no live SNS/SES sends

## Rollback

1. Set action group `DISABLED` on DRAFT
2. `prepare_agent` + `update_agent_alias` without routing pin (creates new version)
3. Or route alias back to version **3** via explicit `routingConfiguration`
