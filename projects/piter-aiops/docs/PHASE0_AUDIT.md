# Phase 0 — Folder & Document Audit

**Project:** `projects/piter-aiops/`  
**Region:** `us-east-1` · **Profile:** `reemmor` · **Account:** `329597159579`

## Key directories (one-line purpose)

| Path | Purpose |
|------|---------|
| `app/` | Flask app: routes, Bedrock clients, workflow, config |
| `action_groups/PITER AiOps-ops/` | Legacy mock-ops Lambda (env status, alerts, create incident) |
| `data/sample_documents/` | KB corpus (runbooks, CSV, PDF, JSON) |
| `data/agent_data/` | Enrichment tool datasets (deploys, catalog, impact) — **created in Phase 2** |
| `docs/` | Setup guides, architecture, cleanup |
| `frontend/` | React 19 SPA (Vite) |
| `infra/` | IAM JSON policies, EC2 user-data, S3 upload script |
| `scripts/` | Agent/KB setup, smoke tests, verify |
| `tests/` | pytest (102+ offline) |

## Existing AWS (pre-upgrade)

| Resource | ID / name | Status |
|----------|-----------|--------|
| Knowledge Base | `RBTJM6NIG9` (`PITER AiOps-course-kb`) | ACTIVE |
| Bedrock Agent | `HH4YGSLZUE` (`agent-quick-reemmnor`) | PREPARED |
| Lambda | `PITER AiOps-actions` | Mock ops handler |
| S3 bucket | `reem-amdocs-ai-artifacts-3331` | Corpus prefix |

## Four data files (enrichment)

| File | Status |
|------|--------|
| `deploys.csv` | **Missing** → `data/agent_data/deploys.csv` |
| `service_catalog.json` | **Missing** → `data/agent_data/service_catalog.json` |
| `impact_matrix.csv` | **Missing** → `data/agent_data/impact_matrix.csv` |
| `incident_history.csv` | **Exists** in `data/sample_documents/` — no `postgres`/`NJ-DGE` rows (append in Phase 2) |

## Runbook doc gaps (KB)

| Runbook | Status |
|---------|--------|
| `runbook_db_cpu.md` | Present |
| `runbook_auth_login.md` | Present (auth) |
| `api_gateway_5xx_runbook.txt` | Present (gateway) |
| `database_connectivity_runbook.md` | Partial (connection) |
| `runbook_settlement.md` | **Missing** — create Phase 1 |
| `runbook_replication_lag.md` | **Missing** — create Phase 1 |
| `runbook_connection_pool.md` | **Missing** — create Phase 1 |

## `.gitignore`

`.env` is gitignored (line 1). Secrets must not be committed.
