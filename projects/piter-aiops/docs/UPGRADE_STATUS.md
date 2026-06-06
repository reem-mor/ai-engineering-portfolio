# Mid-project upgrade — status (2026-06-03)

## Phase 0

- [`PHASE0_AUDIT.md`](PHASE0_AUDIT.md) — folder tree, gaps, live AWS IDs.

## Phase 1 — KB

| Item | Value |
|------|--------|
| KB ID | `RBTJM6NIG9` |
| Data source | `YICXAB6WOG` |
| S3 prefix | `s3://reem-amdocs-ai-artifacts-3331/projects/incidentIQ-midproject/data/sample_documents/` |
| Corpus | **24 files** — canonical `data/sample_documents/` (RB-001…RB-010 merged or added; see `evaluation/CORPUS_RECONCILIATION.md`) |
| Last ingestion | Re-sync after corpus reconciliation (2026-06-06) |
| Retrieval check | Chunk from `runbook_db_cpu.md` (RB-007 Postgres CPU runbook) |

Runbooks added: `runbook_settlement.md`, `runbook_replication_lag.md`, `runbook_connection_pool.md`.

## Phase 2 — Lambdas

| Lambda | Action group | Demo invoke |
|--------|--------------|-------------|
| `iiq-correlate` | `iiq-correlate` | `events/demo_correlate.json` |
| `iiq-context` | `iiq-context` | `events/demo_owner.json`, `demo_impact.json` |
| `iiq-similar` | `iiq-similar` | `events/demo_similar.json` |

Data: `data/agent_data/{deploys.csv,service_catalog.json,impact_matrix.csv}`; NJ-DGE/postgres rows in `incident_history.csv`.

## Phase 3 — MCP

- **Path B (landed):** Action groups on agent `HH4YGSLZUE` — see [`MCP_PATH.md`](MCP_PATH.md) and [`MCP_PATH.json`](MCP_PATH.json).
- **Path A:** AgentCore SDK not in current boto3; Gateway documented for manual enablement.

## Phase 4 — Agent

| Item | Value |
|------|--------|
| Agent ID | `HH4YGSLZUE` |
| Alias | `live` → `O2EM03R4R3` |
| Model | Claude Haiku 4.5 inference profile |
| Instruction | `AGENT_INSTRUCTION` in `app/bedrock_agent_client.py` (synced via `setup_action_group.py` / `ensure_agent_alias.py`) |
| Memory | `sessionAttributes` + `promptSessionAttributes` via `build_session_attributes()` |

## Phase 5 — Flask

- `BedrockAgentClient.ask()` — trace parsing → `RagAnswer.enrichment`
- `/api/workflow/triage` — passes alert context + optional `session_id`
- `build_workflow_payload()` — exposes `enrichment`, `owner_team`, `similar_incidents`

## Phase 6

- pytest: **140 passed** (includes `test_enrichment_tools.py`, `test_agent_client.py`)
- README: mid-project upgrade section + doc links
- Teardown: [`TEARDOWN.md`](TEARDOWN.md) (manual, on go-ahead)

## `.env` (local)

```
BEDROCK_AGENT_ID=HH4YGSLZUE
BEDROCK_AGENT_ALIAS_ID=O2EM03R4R3
BEDROCK_KB_ID=RBTJM6NIG9
```

## Needs input

- Remove duplicate test action group `incidentiq-ops-test` in console when convenient.
- Point alias used by Flask: confirm `BEDROCK_AGENT_ALIAS_ID=O2EM03R4R3` after `ensure_agent_alias.py`.
- Live `invoke_agent` E2E requires AWS creds (`AWS_PROFILE=reemmor`); run `docker compose up --build` for UI on :8080.
