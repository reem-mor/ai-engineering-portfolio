# PITER AWS Phase 6 — Lambda and Action Groups Verification

**Audit date:** 2026-06-08  
**Agent version audited:** 3

## Expected final tool set vs AWS deployment

| PITER final tool | Local folder | AWS deployed | Agent action group | Lambda function |
|------------------|--------------|--------------|--------------------|-----------------|
| piter-recent-deployments | `action_groups/piter-recent-deployments/` | **Via legacy** | `iiq-correlate` | `iiq-correlate` |
| piter-service-context | `action_groups/piter-service-context/` | **Via legacy** | `iiq-context` | `iiq-context` |
| piter-similar-incidents | `action_groups/piter-similar-incidents/` | **Via legacy** | `iiq-similar` | `iiq-similar` |
| piter-escalation | `action_groups/piter-escalation/` | **NOT deployed** | — | — |

## Legacy / additional action groups

| Name | State | Lambda | Classification |
|------|-------|--------|----------------|
| `incidentiq-ops` | ENABLED | `incidentiq-actions` | **Legacy** — recommend disable after demo if unused |
| `incidentiq-ops-test` | DISABLED | — | **Stale** — safe to delete in console later |

## Lambda function details (read-only)

### iiq-correlate

| Field | Value |
|-------|-------|
| Runtime | python3.12 |
| Last modified | 2026-06-04 |
| Handler | `lambda_function.lambda_handler` |
| Timeout / Memory | 15s / 256 MB |
| IAM role | `arn:aws:iam::329***579:role/incidentiq-lambda-role` |
| Environment vars | None configured |
| OpenAPI ops (local) | `correlateDeployments` |
| CloudWatch log group | `/aws/lambda/iiq-correlate` — exists |
| Recent ERROR logs (7d) | None found |

### iiq-context

| Field | Value |
|-------|-------|
| Runtime | python3.12 |
| OpenAPI ops | `lookupOwner`, `scoreBusinessImpact` |
| Recent ERROR logs | None |

### iiq-similar

| Field | Value |
|-------|-------|
| Runtime | python3.12 |
| OpenAPI ops | `findSimilarIncidents` |
| Recent ERROR logs | None |

### incidentiq-actions (incidentiq-ops)

| Field | Value |
|-------|-------|
| Runtime | python3.12 |
| Last modified | 2026-06-03 |
| OpenAPI ops | `getEnvironmentStatus`, `getRecentAlerts`, `createIncident` |
| Recent ERROR logs | None |

## piter-escalation (local only)

- Code exists at `action_groups/piter-escalation/lambda_function.py` with `escalationAction` OpenAPI op.
- **Not deployed** to AWS; **not attached** to Bedrock Agent.
- Tested locally via `tests/test_piter_lambdas.py` and `tests/test_escalation_api.py` (mocked).

### Recommended deployment steps (STOP — requires approval)

1. Package and deploy Lambda `piter-escalation` (python3.12, same role or scoped role).
2. Set env vars: `PITER_NOTIFICATION_MODE`, `PITER_SNS_TOPIC_ARN`, `PITER_SES_SENDER_EMAIL`, confirmation token vars.
3. Run `scripts/setup_action_group.py` (or console) to attach OpenAPI schema to agent v4.
4. Prepare agent and update alias `live` to new version.
5. Run `agent_smoke_test.py` with escalation scenario.

## Local test coverage

| Component | Local tests |
|-----------|-------------|
| iiq-* Lambdas | `tests/test_lambda_action_handler.py`, enrichment tests |
| piter-* Lambdas | `tests/test_piter_lambdas.py` |
| Flask tool merge | `verify_live_demo.py`, agent client unit tests |

## Commands run (read-only)

```powershell
aws lambda list-functions --query "Functions[?contains(FunctionName,'piter') || contains(FunctionName,'iiq') || contains(FunctionName,'incident')]"
aws lambda get-function-configuration --function-name <name>
aws bedrock-agent list-agent-action-groups --agent-id HH4YGSLZUE --agent-version 3
aws logs filter-log-events --log-group-name /aws/lambda/iiq-correlate --filter-pattern ERROR
```
