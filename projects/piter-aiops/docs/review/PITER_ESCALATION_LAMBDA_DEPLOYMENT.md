# PITER Escalation Lambda Deployment

**Date:** 2026-06-08  
**Function:** `piter-escalation`  
**Status:** **Deployed**

## Source

- Handler: `action_groups/piter-escalation/lambda_function.py`
- OpenAPI: `action_groups/piter-escalation/openapi_schema.yaml` (GET `/escalation` with query params)

## Configuration

| Setting | Value |
|---------|--------|
| Runtime | Python 3.12 |
| Architecture | arm64 |
| Memory | 256 MB |
| Timeout | 15 s |
| Role | `incidentiq-lambda-role` |
| Log group | `/aws/lambda/piter-escalation` (14-day retention) |

## Environment (names only; mock-safe values in AWS)

- `PITER_NOTIFICATION_MODE=mock`
- `PITER_ENABLE_LIVE_DISPATCH=false`
- `PITER_NOTIFICATION_REQUIRE_CONFIRMATION=true`
- `PITER_NOTIFICATION_ALLOWLIST` (empty)
- `PITER_NOTIFICATION_CONFIRMATION_TOKEN` (empty)
- `PITER_NOTIFICATION_ALLOWED_SEVERITIES=P1,P2`
- `PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT=1`

## Post-deploy validation

| Test | Result |
|------|--------|
| Preview invoke (Bedrock action event) | **PASS** — masked recipient `ro***ll` |
| Live send without confirmation | **Blocked** (mock mode) |
| Duplicate notification | **Blocked** by idempotency logic |
| Raw contact in Lambda response | **None** (masked) |

## IAM

- Attached managed policy: `PITER-AiOps-Notifications` (SNS/SES scoped; inactive while mock mode)

## Rollback

- Disable action group on agent DRAFT; do not delete function without backup
- Previous state: function did not exist in AWS

## Orchestration

Idempotent deploy: `python scripts/setup_piter_aws_mutations.py --skip-guardrail --skip-alias`
