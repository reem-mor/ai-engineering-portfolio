# PITER Bedrock Agent & KB Audit (Read-Only)

**Region:** us-east-1 | **Profile:** reemmor | **No mutations performed**

## Local code paths

| Path | Module | Purpose |
|------|--------|---------|
| Direct KB RAG | `app/bedrock_client.py` | `retrieve_and_generate` |
| Agent | `app/bedrock_agent_client.py` | `invoke_agent` + trace parse |
| Factory | `app/rag_factory.py` | Select backend from `RAG_BACKEND` |
| Fallback | `app/local_agent.py` | TF-IDF on BedrockError |
| Current `.env` | `RAG_BACKEND=retrieve_and_generate` | Demo-stable 7/7 smoke |

## AWS resources (read-only evidence)

| Resource | ID / name | Status | Config env var |
|----------|-----------|--------|----------------|
| Knowledge Base | `RBTJM6NIG9` | Active | `PITER_BEDROCK_KB_ID` |
| Data source | `YICXAB6WOG` (`piter-aiops-runbooks-datasource`) | AVAILABLE | `PITER_BEDROCK_DATA_SOURCE_ID` |
| Agent | `HH4YGSLZUE` | Name: **`incidentiq-triage-agent`** | `PITER_BEDROCK_AGENT_ID` |
| Alias `live` | `O2EM03R4R3` | PREPARED, version **3** | `PITER_BEDROCK_AGENT_ALIAS_ID` |
| Model (local .env) | Haiku 4.5 inference profile | Smoke 7/7 | `PITER_BEDROCK_MODEL_ARN` |

## Agent ↔ KB association

KB `RBTJM6NIG9` is **ENABLED** on agent DRAFT (and prepared versions via alias).

## Action groups on agent

| Name | State | Maps to PITER tool |
|------|-------|-------------------|
| `iiq-correlate` | ENABLED | recent deployments |
| `iiq-context` | ENABLED | service context |
| `iiq-similar` | ENABLED | similar incidents |
| `incidentiq-ops` | ENABLED | Extra ops API (not in core 4) |
| `incidentiq-ops-test` | DISABLED | Remove candidate |

**Missing on agent:** `piter-escalation` / fourth core tool as action group (escalation handled via Flask `notification_dispatch`).

## Lambda functions in account

| Function | Runtime |
|----------|---------|
| `iiq-correlate` | python3.12 |
| `iiq-context` | python3.12 |
| `iiq-similar` | python3.12 |

No `piter-escalation` Lambda deployed in list output.

## Issues (report only — fix requires approval)

1. **Branding:** Agent name and alias description still say IncidentIQ.
2. **Fourth tool:** Escalation not wired as Bedrock action group in AWS.
3. **Fifth group:** `incidentiq-ops` may confuse teacher requirement "exactly four tools".
4. **`.env.example` default:** `RAG_BACKEND=agent` vs production demo using `retrieve_and_generate`.

## Suggested fix commands (DO NOT RUN without approval)

```bash
# Sync agent instruction + ensure alias (already run in prior session)
py -3.12 scripts/ensure_agent_alias.py --agent-id HH4YGSLZUE

# Deploy piter-escalation + register action group
py -3.12 scripts/setup_enrichment_lambdas.py  # review script first

# KB ingestion after S3 sync
py -3.12 scripts/sync_kb_and_wait.py
```
