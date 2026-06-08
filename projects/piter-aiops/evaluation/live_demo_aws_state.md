# Live Demo — AWS Resource State (read-only verification)

Captured: 2026-06-07 (us-east-1, account `329597159579`, caller `admin-reem`)

This is a read-only snapshot of the EXISTING AWS resources used by the optional
"live on Bedrock" path. No resources were created or deleted to produce it.

**Branding:** User-facing product name is **PITER AiOps**. Several AWS console labels still use early working titles (`incidentiq-*`, `iiq-*`) from before the rename. The active S3 corpus prefix is `projects/piter-aiops/` — not the legacy `incident-rag-bedrock` path.

## Bedrock Knowledge Base

| Field | Value |
|-------|-------|
| KB ID | `RBTJM6NIG9` |
| Name | `incidentiq-course-kb` (AWS console name; app branding is PITER AiOps) |
| Status | `ACTIVE` |
| Data source ID | `YICXAB6WOG` |
| Data source name | `piter-aiops-runbooks-datasource` |
| Data source status | `AVAILABLE` |
| S3 prefix | `s3://reem-amdocs-ai-artifacts-3331/projects/piter-aiops/data/sample_documents/` (24 objects) |
| Last ingestion | `5Q3KWI4RVZ` — `COMPLETE` |

## Bedrock Agent

| Field | Value |
|-------|-------|
| Agent ID | `HH4YGSLZUE` |
| Name | `incidentiq-triage-agent` |
| Status | `PREPARED` |
| Model | `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Alias ID | `O2EM03R4R3` (name `live`) |
| Alias status | `PREPARED` |
| Alias routing | agentVersion **`3`** (updated from v1 on 2026-06-06) |
| Instruction | 1628 chars — synced from `app/bedrock_agent_client.py` `AGENT_INSTRUCTION` |

## Action groups (agent version 3)

| Action group | State | Lambda |
|--------------|-------|--------|
| `iiq-correlate` | ENABLED | `iiq-correlate` |
| `iiq-context` | ENABLED | `iiq-context` |
| `iiq-similar` | ENABLED | `iiq-similar` |
| `incidentiq-ops` | ENABLED | `incidentiq-actions` |
| `incidentiq-ops-test` | **DISABLED** (stale — safe to delete in console) |

**Note:** Local `action_groups/piter-*` folders mirror enrichment for Flask/MCP; AWS still uses `iiq-*` names until a rename deploy is run.

## Guardrails

| Check | Result |
|-------|--------|
| Bedrock Guardrails (account) | **None configured** |
| App operator guardrails (`app/guardrails.py`) | **Active** — blocks FLUSHALL/DROP/TRUNCATE/mass-delete prompts before Bedrock |

## EC2 demo host

| Field | Value |
|-------|-------|
| Tagged instances (`Project=piter-aiops`) | **None** |
| Result | EC2 proof unavailable; use **local Docker** (`docker compose up` → `:8080/console`) |

## Live verification (2026-06-07)

| Script | Result |
|--------|--------|
| `scripts/kb_smoke_test.py` | **7/7 PASS** — grounded runbook answers + off-topic refusal |
| `scripts/agent_smoke_test.py` | **7/7 PASS** — `retrieve_and_generate` path |
| `scripts/verify_live_demo.py` | **29/29 PASS** — live Bedrock + local fallback + session memory |
| `invoke_agent` spot check | **OK** — citations + enrichment (deployments, owner, similar incidents) |
| `pytest` | **246/246 PASS** (after notification-mode test fix) |
