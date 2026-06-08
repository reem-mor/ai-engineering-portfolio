# PITER AWS Phase 3 — Bedrock Knowledge Base Verification

**Audit date:** 2026-06-08  
**KB ID:** `RBTJM6NIG9`  
**Profile / region:** `reemmor` / `us-east-1`

## KB summary

| Field | Value |
|-------|-------|
| Name | `incidentiq-course-kb` (legacy console name; corpus is PITER-branded) |
| Status | **ACTIVE** |
| Role ARN | `arn:aws:iam::329***579:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_2q8xn` |
| Storage type | **S3_VECTORS** (index in `bedrock-knowledge-base-kpjyt6`) |
| Embedding model | `amazon.titan-embed-text-v2:0` |
| Data source ID | `YICXAB6WOG` |
| Data source name | `piter-aiops-runbooks-datasource` |
| Data source status | **AVAILABLE** |
| S3 bucket | `reem-amdocs-ai-artifacts-3331` |
| S3 prefix | `projects/piter-aiops/data/sample_documents/` |
| Chunking | Fixed size, 500 tokens, 15% overlap |

## Latest ingestion jobs

| Job ID | Status | Notes |
|--------|--------|-------|
| `5Q3KWI4RVZ` | COMPLETE | 24 docs scanned; 1 new indexed |
| `340P2YZ4YF` | COMPLETE | 20 scanned; **20 failed**, 17 deleted — review if unexpected |
| `H3NES7CPJO` | COMPLETE | 8 new, 1 modified |

## Corpus alignment with `knowledge_base/` intent

- S3 prefix contains **28 objects** — runbooks (`runbook_*.md`), policies (`escalation_policy.pdf`), incident history, postmortems, tier-1 guide.
- Matches local `data/sample_documents/` and `knowledge_base/runbooks/` intent (NOC/SRE triage corpus).
- No `IncidentIQ`-only filenames in S3 listing; content is PITER/runbook oriented.

## Demo retrieval queries (read-only `retrieve` API)

### Query 1: postgres CPU high runbook

| Metric | Result |
|--------|--------|
| Result count | **5** |
| Top sources | `runbook_db_cpu.md` (×2 chunks), `database_connectivity_runbook.md`, `runbook_replication_lag.md`, `runbook_connection_pool.md` |
| Relevance | **High** — RB-007 Postgres CPU runbook ranked first (score ~0.63) |
| Citation support | **Yes** — directly supports P2/P1 DB triage |

### Query 2: bet-service GIB-UKGC outage

| Metric | Result |
|--------|--------|
| Result count | **≥3** (CLI encoding error on full text; URIs confirmed) |
| Top sources | `runbook_bet_service_outage.md` (top hit, score ~0.62) |
| Relevance | **High** — primary bet-service outage runbook |
| Citation support | **Yes** |

### Query 3: escalation policy P1

| Metric | Result |
|--------|--------|
| Result count | **3+** |
| Top sources | `tier1_escalation_guide.md`, `escalation_policy.pdf`, `runbook_bet_service_outage.md` |
| Relevance | **High** — P1 definitions and paging chain present |
| Citation support | **Yes** |

### Query 4: similar incident bet-service 100% error rate

| Metric | Result |
|--------|--------|
| Result count | **≥1** |
| Top sources | `runbook_bet_service_outage.md` (score ~0.54) |
| Relevance | **Moderate–High** — runbook covers outage pattern; similar incidents also available via Lambda/history CSV |
| Citation support | **Yes** for runbook; enrichment tools add `incident_history.csv` |

## Commands run (read-only)

```powershell
aws bedrock-agent get-knowledge-base --knowledge-base-id RBTJM6NIG9
aws bedrock-agent list-data-sources --knowledge-base-id RBTJM6NIG9
aws bedrock-agent get-data-source --knowledge-base-id RBTJM6NIG9 --data-source-id YICXAB6WOG
aws bedrock-agent list-ingestion-jobs --knowledge-base-id RBTJM6NIG9 --data-source-id YICXAB6WOG --max-results 3
aws bedrock-agent-runtime retrieve --knowledge-base-id RBTJM6NIG9 --retrieval-query "text=..." --retrieval-configuration '{"vectorSearchConfiguration":{"numberOfResults":5}}'
```

## Gaps

1. Ingestion job `340P2YZ4YF` reported **20 failed** documents — worth monitoring; did not block retrieval during audit.
2. Console KB name still says `incidentiq-course-kb` (cosmetic; no functional impact).
