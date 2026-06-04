# Live Demo — AWS Resource State (read-only verification)

Captured: 2026-06-04 (us-east-1, account `329597159579`, caller `admin-reem`)

This is a read-only snapshot of the EXISTING AWS resources used by the optional
"live on Bedrock" path. No resources were created or deleted to produce it.

## Bedrock Knowledge Base

| Field | Value |
|-------|-------|
| KB ID | `RBTJM6NIG9` |
| Name | `incidentiq-course-kb` |
| Status | `ACTIVE` |
| Updated | 2026-05-28T08:11:22Z |
| Data source ID | `YICXAB6WOG` |
| Data source name | `reem-amdocs-ai-artifacts-3331` |
| Data source status | `AVAILABLE` |

## Bedrock Agent

| Field | Value |
|-------|-------|
| Agent ID | `HH4YGSLZUE` |
| Name | `agent-quick-reemmnor` |
| Status | `PREPARED` |
| Model | `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Prepared at | 2026-06-03T13:32:36Z |
| Alias ID | `O2EM03R4R3` (name `live`) |
| Alias status | `PREPARED` |
| Alias routing | agentVersion `1` |

## Action Group Lambdas

| Function | State | Runtime | Last modified |
|----------|-------|---------|---------------|
| `iiq-correlate` | Active | python3.12 | 2026-06-03T13:30:54Z |
| `iiq-context` | Active | python3.12 | 2026-06-03T13:30:59Z |
| `iiq-similar` | Active | python3.12 | 2026-06-03T13:31:02Z |

## EC2 demo host

| Field | Value |
|-------|-------|
| Expected instance | `i-016d77ef747791213` |
| Result | **Not found** — instance no longer exists |
| Non-terminated instances in account | none |

**Implication:** the EC2 "it's live on a server" proof is unavailable. The
primary and recommended demo surface is **local Docker** (`docker compose up`
-> http://localhost:8080/console), which is fully validated. Re-launching EC2
would create new paid infra and is therefore out of scope for this task unless
explicitly approved (helper: `scripts/launch_ec2_demo.ps1`).

## Existing-resource operations performed (allowed)

Executed 2026-06-04 against the EXISTING resources only — no new infra:

| Operation | Result |
|-----------|--------|
| Re-sync KB ingestion (`start-ingestion-job` `SX9IOIRMIT`) | `COMPLETE` — 17 docs scanned, 0 new / 0 modified / 0 failed (KB already current) |
| `PrepareAgent` `HH4YGSLZUE` | `PREPARED` at 2026-06-04T07:45:41Z |
| Verify alias `O2EM03R4R3` (`live`) | `PREPARED`, routing to agentVersion `1` — current, no repoint / no new alias needed |
| Redeploy lambdas (`update-function-code`) | `iiq-correlate`, `iiq-context`, `iiq-similar` all `Active`, lastModified 2026-06-04T07:46Z |

Helper added: `scripts/redeploy_lambdas.py` (code-only update of existing functions).

## Model access (previous 403 — RESOLVED)

The `RetrieveAndGenerate` 403 recorded in `docs/READONLY_VERIFICATION.md` is no
longer reproducible. Verified live on 2026-06-04:

| Check | Result |
|-------|--------|
| Inference profile `us.anthropic.claude-haiku-4-5-20251001-v1:0` | `ACTIVE` |
| `invoke_agent` via alias `live` (the app's demo path, `RAG_BACKEND=agent`) | **OK** — returned a grounded RB-007 runbook answer (1026 chars) |
| `retrieve_and_generate` against KB `RBTJM6NIG9` | **OK** — returned a grounded answer citing the Postgres CPU runbook |

Conclusion: the live Bedrock path is functional. Model access does **not** need
manual enablement for this account/region. The local fallback remains in place
regardless, so the demo is safe even if Bedrock degrades on the day.
