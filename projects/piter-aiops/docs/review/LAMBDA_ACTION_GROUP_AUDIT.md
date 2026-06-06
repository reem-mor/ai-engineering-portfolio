# PITER AiOps — Lambda & Action Group Audit

Read-only audit · 2026-06-06

## Function inventory

| Function | Purpose | Input | Output | Bedrock action group | IAM | Tests | Live status |
| -------- | ------- | ----- | ------ | -------------------- | --- | ----- | ----------- |
| `iiq-correlate` | Recent deploy correlation | `service`, `environment`, `alert_time`, `lookback_hours` | `deployments[]`, `suspect_deployment`, `reason` | `iiq-correlate` → `POST /correlate` | Documented in `docs/bedrock_action_group_setup.md` | `events/demo_correlate.json`; mirrors `app/enrichment_tools` | **Active** per `evaluation/live_demo_aws_state.md` |
| `iiq-context` | Owner + business impact | `POST /owner`, `POST /impact` params | Owner team, on-call, escalation chain; SLA/revenue impact | `iiq-context` | Same | Demo events referenced in `UPGRADE_STATUS.md` | **Active** |
| `iiq-similar` | Similar past incidents | `service`, `symptom`, `environment`, `top_k` | `similar_incidents[]` with MTTR/root cause | `iiq-similar` → `POST /similar` | Same | Enrichment parity tests | **Active** |
| `PITER AiOps-actions` (incidentiq-ops) | Mock NOC ops (GIB/MGM status) | OpenAPI paths in `incidentiq-ops/openapi_schema.yaml` | Mock environment status/alerts | `PITER AiOps-ops` | Same | `tests/test_lambda_action_handler.py` | Optional 4th function |

**Count:** 3 required enrichment Lambdas + 1 optional ops mock = **4 total** (meets teacher 3–4 requirement).

## Architecture split (important for demo honesty)

| Path | Who runs the 4 tools? |
|------|---------------------|
| `/api/triage` with `retrieve_and_generate` | **App layer** — `app/services/tool_router.py` → `app/enrichment_tools.py` (deterministic) |
| `/api/triage` with `RAG_BACKEND=agent` | **Bedrock Agent** may invoke action-group Lambdas during `invoke_agent`; app **also** runs local tools in `run_triage` today |

The live `/console` demo always shows tool outputs (owner, impact, similar, correlate) because `run_triage` calls `run_plan(decide_tools(alert))` regardless of RAG backend. Agent action groups are **implemented and deployed** but are not the sole source of tool data during the default triage API path.

## Per-function quality

| Criterion | Assessment |
|-----------|------------|
| Single responsibility | **Pass** — one domain per Lambda |
| Action-group event parsing | **Pass** — `_params_to_dict`, `_respond` pattern in `lambda_function.py` |
| Parameter validation | Basic (missing service → error dict) |
| Stable JSON output | **Pass** |
| Structured logging | **Pass** — `logger.info` with event JSON |
| Credentials in code | **None** |
| Destructive actions | **None** — read-only enrichment |
| Timeout/memory | Default Lambda; recommend 256MB / 30s documented in setup guides |

## Connection to Agent

| Item | Status |
|------|--------|
| Agent ID in `.env` | Configured |
| Action groups attached | Documented deployed (`iiq-*`) |
| OpenAPI in S3 | Per `docs/MCP_PATH.md` |
| Live `invoke_agent` tool traces | Parsed in `BedrockAgentClient._merge_action_output` |
| End-to-end agent+tools test | `scripts/agent_smoke_test.py --ops` (3/3 per eval) |

## Redeploy / setup scripts

- `scripts/setup_enrichment_lambdas.py`
- `scripts/redeploy_lambdas.py`
- `scripts/setup_action_group.py` (also handles `incidentiq-ops`)
