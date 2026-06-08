# PITER Lambda & Action Group Audit

## Target four tools (course requirement)

| PITER name | Folder | OpenAPI | Lambda handler | AWS deployed |
|------------|--------|---------|----------------|--------------|
| piter-recent-deployments | `action_groups/piter-recent-deployments/` | Yes | `lambda_function.py` | As **`iiq-correlate`** |
| piter-service-context | `action_groups/piter-service-context/` | Yes | Yes | As **`iiq-context`** |
| piter-similar-incidents | `action_groups/piter-similar-incidents/` | Yes | Yes | As **`iiq-similar`** |
| piter-escalation | `action_groups/piter-escalation/` | Yes | Yes | **Not listed in AWS** |

## Legacy parallel tree

| Folder | Role |
|--------|------|
| `action_groups/iiq-correlate/` | Deployed Lambda source + duplicate data |
| `action_groups/iiq-context/` | Deployed |
| `action_groups/iiq-similar/` | Deployed |
| `action_groups/incidentiq-ops/` | Fifth action group on agent — mock env status |

## Tests

| Test file | Coverage |
|-----------|----------|
| `tests/test_piter_lambdas.py` | piter-* handlers, escalation safety |
| `tests/test_lambda_action_handler.py` | incidentiq-ops |
| `tests/test_enrichment_tools.py` | App-level tool parity |

## Escalation Lambda safety (`piter-escalation`)

- Mock/preview by default via env
- Allowlist + confirmation token enforced in app route
- In-process idempotency set — not durable across cold starts

## OpenAPI / schemas

- Each `piter-*` has `openapi_schema.yaml`
- S3 agent schemas referenced in `docs/MCP_PATH.md` under `agent/iiq-*/`

## Gaps

1. Deploy `piter-escalation` and register action group (AWS approval)
2. Deduplicate `iiq-*/enrichment_tools.py` vs `app/enrichment_tools.py`
3. Fix `incidentiq-ops` environment code validation
4. Remove or disable `incidentiq-ops-test` on agent
