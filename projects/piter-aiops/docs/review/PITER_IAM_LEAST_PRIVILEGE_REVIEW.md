# PITER IAM Least Privilege Review

**Date:** 2026-06-08

## Roles reviewed

### `incidentiq-agent-role`

| Policy | Type | Notes |
|--------|------|-------|
| `incidentiq-agent-resource` | Inline | KB retrieve, Lambda invoke (incl. `piter-escalation`), S3 OpenAPI read, inference profile, **ApplyGuardrail** |

**Recommendation:** Acceptable for demo. Tighten foundation-model ARNs to single inference profile in production.

### `incidentiq-lambda-role`

| Policy | Type | Notes |
|--------|------|-------|
| `incidentiq-lambda-execution` | Inline | CloudWatch Logs |
| `PITER-AiOps-Notifications` | Managed | SNS/SES scoped |

**Recommendation:** Notifications policy only needed when live dispatch enabled.

## Changes applied

- Added `piter-escalation` to agent Lambda invoke list
- Added `bedrock:ApplyGuardrail` + `bedrock:GetGuardrail` for guardrail `rti921amc6u3`

## Not changed

- Admin user `admin-reem` still used for local dev (broad access)
- No IAM roles deleted

## Proposed production hardening (not applied)

- Separate agent vs Lambda roles per tool
- Resource-tag condition keys on SNS topic ARN
- Deny `sns:Publish` when `PITER_ENABLE_LIVE_DISPATCH` false (SCP/lambda env guard)
