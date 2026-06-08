# Cleanup log — 2026-05-31 (S3/KB alignment + EC2 relaunch)

> Product branding is **PITER AiOps** (`projects/piter-aiops/`). Resource names below (`incident-rag-*`, `IncidentRagBedrock*`) are from the first milestone and kept here as an audit trail.

Resources created for assignment proof and removed the same day.

## Deleted

| Resource | ID / name | Action |
|----------|-----------|--------|
| EC2 instance | `i-03d3c5a59e849e5cf` (`incident-rag-demo`) | Terminated |
| Security group | `sg-0b405b6a42325979e` (`incident-rag-sg`) | Deleted |
| IAM instance profile | `incident-rag-ec2-profile` | Deleted |
| IAM role | `incident-rag-ec2-role` | Deleted (inline policy removed first) |
| ECR repository | `incident-rag-bedrock` | Deleted 2026-06-01 (`--force`); deploy path uses GHCR, repo was leftover |

## Public URL used during testing (now offline)

`http://ec2-100-53-32-194.compute-1.amazonaws.com/`

Validated: `/health` → `{"status":"ok"}`, grounded `/ask` with citations, off-topic refusal, MVP workflow triage.

## Retained (shared / reusable)

| Resource | Notes |
|----------|--------|
| Bedrock KB `RBTJM6NIG9` | Data source prefix `projects/piter-aiops/data/sample_documents/`; re-synced 2026-06-06 (job `G4U131YDRV`) — **24 docs scanned, 4 new, 8 modified, 0 failed** after RB corpus reconciliation |
| S3 bucket `reem-amdocs-ai-artifacts-3331` | Canonical corpus at `projects/piter-aiops/data/sample_documents/` (see `evaluation/CORPUS_RECONCILIATION.md`) |
| Bedrock KB execution role S3 policy | `AmazonBedrockS3PolicyForKnowledgeBase_2q8xn` v2 — includes new prefix (see `infra/bedrock_kb_s3_policy.json`) |

## Prior cleanup (same day, earlier session)

| Resource | ID / name |
|----------|-----------|
| EC2 instance | `i-0ff0a902311a5943b` |
| Security group | `sg-052717984128f7617` |

Previous public URL: `http://ec2-13-222-142-122.compute-1.amazonaws.com/`
