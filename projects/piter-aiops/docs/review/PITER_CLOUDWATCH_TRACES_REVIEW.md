# PITER CloudWatch Logs and Traces Review

**Date:** 2026-06-08

## Lambda log groups

| Log group | Retention | Notes |
|-----------|-----------|-------|
| `/aws/lambda/piter-escalation` | **14 days** | Set during mutation |
| `/aws/lambda/iiq-context` | **14 days** | |
| `/aws/lambda/iiq-correlate` | **14 days** | |
| `/aws/lambda/iiq-similar` | **14 days** | |
| `/aws/lambda/incidentiq-actions` | **14 days** | |

## Log safety

- Escalation Lambda logs use masked recipients only
- No raw phone/email observed in recent preview invokes
- No secrets in structured app logs (pytest guardrail tests pass)

## Bedrock traces

- Agent trace log groups not found under `/aws/bedrock*` for this agent ID
- Orchestration observations mined in-app via `bedrock_agent_client.py` when enabled

## Errors

- Pre-guardrail IAM: `accessDeniedException` on invoke — **resolved** with ApplyGuardrail permission
- No unresolved action-group OpenAPI errors after GET schema fix

## Recommendations

- Enable Bedrock model invocation logging for audit if required by course rubric
- Add correlation ID in Lambda structured logs (future)
