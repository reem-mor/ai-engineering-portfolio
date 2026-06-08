# PITER KB and S3 Alignment

**Date:** 2026-06-08  
**Knowledge Base:** `RBTJM6NIG9` (`incidentiq-course-kb`) — **ACTIVE**

## Association

| Agent version | KB state |
|---------------|----------|
| DRAFT | ENABLED |
| 6 (live) | ENABLED |

## Data source

| Field | Value |
|-------|--------|
| ID | `YICXAB6WOG` |
| Name | `piter-aiops-runbooks-datasource` |
| S3 bucket | `reem-amdocs-ai-artifacts-3331` |
| Prefix | `projects/piter-aiops/data/sample_documents/` |

## S3 layout

| Prefix | Contents |
|--------|----------|
| `projects/piter-aiops/data/sample_documents/` | KB corpus (runbooks, policies, CSVs) |
| `agent/*/openapi_schema.yaml` | Action group OpenAPI (incl. `piter-escalation`) |
| `knowledge-base/` | **Empty** — not used |

## Retrieval checks

Direct KB and agent paths return bet-service outage runbook, escalation policy, and similar incident content. No secrets observed in sample documents.

## Ingestion note

Job `340P2YZ4YF` (2026-06-06) completed with document failures (20 failed). Non-blocking for demo; re-sync recommended before production.

## Sync action

No S3 upload performed in this mutation window — local corpus already aligned with inclusion prefix. To sync:

1. `python scripts/upload_kb_docs.py` (if available) or `aws s3 sync data/sample_documents/ s3://.../projects/piter-aiops/data/sample_documents/`
2. Start ingestion job on data source `YICXAB6WOG`
3. Re-run retrieval smoke

## Rollback

Do not delete S3 objects without versioned backup. Retain prior prefix contents.
