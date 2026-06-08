# PITER AiOps Lambda Action Group

Bedrock Agent action group for live NOC operations (environment status, alerts, incident creation).

> **Folder name:** `incidentiq-ops` is a legacy directory name (early **IncidentIQ** working title). Product branding is **PITER AiOps**. In AWS the action group is still `incidentiq-ops` with Lambda `incidentiq-actions` until an optional rename deploy.

## Files

| File | Purpose |
|------|---------|
| `lambda_function.py` | Lambda handler — routes by `apiPath` + `httpMethod`, returns Bedrock-compliant responses |
| `openapi_schema.yaml` | OpenAPI 3.0 spec the agent uses to discover and invoke tools |

## Actions

| Action | Method/Path | Type |
|--------|-------------|------|
| Get environment status | `GET /environments/{environment}/status` | Read |
| List recent alerts | `GET /environments/{environment}/alerts?hours=N` | Read |
| Open incident ticket | `POST /incidents` | Write |

Backends are mocked in-memory. Replace `MOCK_STATUSES`, `MOCK_ALERTS`, and `create_incident` for production.

## Deploy (automated)

From project root:

```powershell
python scripts/setup_action_group.py --dry-run
python scripts/setup_action_group.py
```

See [`docs/bedrock_action_group_setup.md`](../../docs/bedrock_action_group_setup.md) for IAM roles, manual fallback, and test prompts.

## Test prompts (after Prepare)

- "What's the current status of GIB?"
- "Show me alerts in GIB from the last 6 hours."
- "Open a P2 incident in GIB titled 'replication lag investigation'." — agent should confirm before write.
