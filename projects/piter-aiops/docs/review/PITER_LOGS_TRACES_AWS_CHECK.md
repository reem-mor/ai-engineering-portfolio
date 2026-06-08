# PITER AWS Phase 11 — CloudWatch Logs and Traces

**Audit date:** 2026-06-08  
**Window:** Last 7 days (Lambda ERROR filter)

## Lambda log groups inspected

| Log group | Exists | Recent ERROR events |
|-----------|--------|---------------------|
| `/aws/lambda/iiq-correlate` | Yes | **None** |
| `/aws/lambda/iiq-context` | Yes | **None** |
| `/aws/lambda/iiq-similar` | Yes | **None** |
| `/aws/lambda/incidentiq-actions` | Yes | **None** |

## Bedrock / application logs

| Source | Notes |
|--------|-------|
| EC2 app logs | N/A — no EC2 instance |
| Local Flask/gunicorn | Docker container stdout (not exported to CloudWatch in local mode) |
| Bedrock Agent traces | Available in `invoke_agent` response stream (orchestration traces parsed in `bedrock_agent_client.py`); not persisted to CloudWatch by default |

## Errors observed during local verification (sanitized)

| Phase | Error | Root cause | Fix type |
|-------|-------|------------|----------|
| `verify_live_demo.py` Phase B | `ResourceNotFoundException: Knowledge Base with id ZZZZZZZZZZ does not exist` | **Intentional** bad KB ID for fallback test | Local test only — expected |
| Phase A live path | None | — | — |

## Error categories checked

| Category | Found in Lambda logs |
|----------|----------------------|
| Bedrock throttling | No |
| Permission denied | No |
| ResourceNotFound | No |
| Invalid environment code | No |
| Action group invocation failures | No |
| SNS/SES errors | Not in Lambda logs (dispatch is app-side) |
| Legacy IncidentIQ strings | No errors; legacy names appear in resource labels only |

## Trace availability

- **Agent orchestration traces:** Parsed client-side from `invoke_agent` event stream.
- **Not configured:** X-Ray, CloudWatch Logs subscription for Bedrock Agent, or centralized trace export.

## Recommendations (no mutation)

1. Enable Bedrock Agent logging to CloudWatch for demo debugging (optional).
2. Add metric alarm on Lambda `Errors` > 0 for action groups.

## Commands run (read-only)

```powershell
aws logs filter-log-events --log-group-name /aws/lambda/iiq-correlate --filter-pattern ERROR --limit 3
# (repeated for iiq-context, iiq-similar, incidentiq-actions)
```
