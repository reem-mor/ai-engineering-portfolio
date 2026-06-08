# PITER AWS Mutation Preflight

**Date:** 2026-06-08  
**Scope:** `projects/piter-aiops` only  
**Profile:** `reemmor` · **Region:** `us-east-1` · **Account:** `329***579`

## Git baseline

| Item | Value |
|------|--------|
| Branch | `main` |
| Status | Modified app/bedrock client + tests; new mutation script and review docs pending commit |

## Local baseline (pre-mutation)

| Check | Result |
|-------|--------|
| `python -m pytest` | **271/271 PASS** (Python 3.12) |
| `python scripts/verify_live_demo.py` | **29/29 PASS** |

## Environment variable names (no values)

Loaded from `.env` / `.env.example` names only:

- `PITER_AWS_REGION`, `PITER_USE_BEDROCK`, `RAG_BACKEND`
- `PITER_BEDROCK_KB_ID`, `PITER_BEDROCK_DATA_SOURCE_ID`, `PITER_BEDROCK_MODEL_ARN`
- `PITER_BEDROCK_AGENT_ID`, `PITER_BEDROCK_AGENT_ALIAS_ID`
- `PITER_S3_BUCKET`, `PITER_S3_PREFIX`
- `PITER_NOTIFICATION_MODE`, `PITER_ENABLE_LIVE_DISPATCH`, `PITER_NOTIFICATION_REQUIRE_CONFIRMATION`
- `PITER_NOTIFICATION_CONFIRMATION_TOKEN`, `PITER_NOTIFICATION_ALLOWLIST`
- `AWS_PROFILE`

## AWS state before mutations

| Resource | Pre-mutation |
|----------|----------------|
| Agent ID | `HH4YGSLZUE` |
| Alias `live` | `O2EM03R4R3` → version **3** |
| KB | `RBTJM6NIG9` ENABLED |
| Guardrail | `rti921amc6u3` READY, **not attached** to live version |
| Action groups (v3) | `iiq-*`, `incidentiq-ops` ENABLED, no `piter-escalation` |
| Lambda | `iiq-*`, `incidentiq-actions`; **`piter-escalation` not deployed** |
| SNS | `piter-aiops-escalation` |
| SES | Sandbox; verified senders present |
| S3 bucket | `reem-amdocs-ai-artifacts-3331` |
| KB prefix | `projects/piter-aiops/data/sample_documents/` |

## Snapshots

JSON exports (no secrets): [`aws_snapshot/`](aws_snapshot/)

## Rollback reference

- Alias routing history: v1 → v2 → v3 (pre-mutation live)
- Re-enable `incidentiq-ops` on DRAFT, prepare, update alias without pinning old version
- Detach guardrail via `update_agent` without `guardrailConfiguration`, prepare, new alias version
