# Knowledge Base Corpus — Incident Operations

These 10 documents form the source corpus for the Bedrock Knowledge Base.
They are deliberately written as if they came from a real NOC / SRE wiki — concrete commands, specific thresholds, named services — so the KB can return useful, grounded answers.

## Dataset card

| Field | Value |
|---|---|
| **Name** | Incident Operations knowledge-base corpus |
| **Domain** | NOC / DevOps / SRE incident response (runbooks, SOPs, policies, history) |
| **Documents** | 10 files · 5 formats (MD, TXT, CSV, DOCX, PDF) |
| **Provenance** | **Synthetic** — hand-authored for this course in `scripts/build_corpus.py`. Not scraped or copied from any third party. |
| **PII / secrets** | **None.** All service names, hostnames, incident IDs, and people/roles are fictional. No real customer data, credentials, or secrets. |
| **Intended use** | Source corpus for a grounded RAG demo: retrieve-and-cite from these docs, refuse when a question is out of corpus. Educational only. |
| **License / usage** | Course coursework — free to read and reproduce within the course context. |
| **Refresh** | Deterministic: re-run `python scripts/build_corpus.py` to regenerate every file. |

## Format coverage (assignment requirement)

| Format | Count | Files |
|---|---|---|
| **MD** | 3 | `auth_service_runbook.md`, `database_connectivity_runbook.md`, `monitoring_alerts_reference.md` |
| **TXT** | 2 | `api_gateway_5xx_runbook.txt`, `payment_service_latency_runbook.txt` |
| **CSV** | 1 | `incident_history.csv` (30 rows of past incidents) |
| **DOCX** | 2 | `deployment_rollback_sop.docx`, `postmortem_template.docx` |
| **PDF** | 2 | `escalation_policy.pdf`, `on_call_handoff_checklist.pdf` |

All five formats supported by the Bedrock S3 connector are represented.

## How the corpus was built

Run once (generates all 10 files from source code):

```bash
pip install reportlab python-docx
python scripts/build_corpus.py
```

Output lands in this directory. The script is checked in so the corpus is reproducible — if you want to add or edit documents, edit `scripts/build_corpus.py` and re-run.

## Topic coverage (what questions the KB can answer)

| Document | Sample question it covers |
|---|---|
| `auth_service_runbook.md` | "How do I triage an authentication service incident?" |
| `database_connectivity_runbook.md` | "What checks do I run when Postgres connections are failing?" |
| `monitoring_alerts_reference.md` | "What does the AuthGlobalErrorRateCritical alert mean and what do I do?" |
| `api_gateway_5xx_runbook.txt` | "API Gateway is returning 5xx storms — what's the runbook?" |
| `payment_service_latency_runbook.txt` | "How do I fail over to the backup payment provider?" |
| `incident_history.csv` | "What was the root cause of INC-2025-022?" / "How many P1 incidents were caused by auth-api in 2025?" |
| `deployment_rollback_sop.docx` | "When should I roll back a deployment vs. roll forward?" |
| `postmortem_template.docx` | "What sections does a postmortem need?" |
| `escalation_policy.pdf` | "What's the difference between P1 and P2 severity?" |
| `on_call_handoff_checklist.pdf` | "What should I do at the start of an on-call shift?" |

## Per-file inventory

| File | Format | Size | Notes |
|---|---|---|---|
| `auth_service_runbook.md` | MD | ~3.0 KB | Auth-service triage: scope, deploy check, OIDC, recovery |
| `database_connectivity_runbook.md` | MD | ~1.8 KB | Postgres connectivity checks (refused / too many connections / SSL) |
| `monitoring_alerts_reference.md` | MD | ~1.4 KB | Alert names → meaning → first action |
| `api_gateway_5xx_runbook.txt` | TXT | ~1.8 KB | Gateway 5xx storm runbook |
| `payment_service_latency_runbook.txt` | TXT | ~1.6 KB | Payment latency + backup-provider failover |
| `incident_history.csv` | CSV | ~3.3 KB | **30 rows** of past incidents (schema below) |
| `deployment_rollback_sop.docx` | DOCX | ~37 KB | Roll back vs. roll forward decision SOP |
| `postmortem_template.docx` | DOCX | ~37 KB | Blameless postmortem section template |
| `escalation_policy.pdf` | PDF | ~3.0 KB | P1–P4 severity definitions + paging ladder |
| `on_call_handoff_checklist.pdf` | PDF | ~2.9 KB | Start-of-shift on-call checklist |

### `incident_history.csv` schema

`incident_id, date, severity, service, root_cause, mttr_minutes, customer_impact`

| Column | Type | Example |
|---|---|---|
| `incident_id` | string | `INC-2025-001` |
| `date` | date (YYYY-MM-DD) | `2025-01-08` |
| `severity` | enum P1–P3 | `P1` |
| `service` | string | `auth-api` |
| `root_cause` | string | `Bad config rollout disabled session cookie` |
| `mttr_minutes` | integer | `47` |
| `customer_impact` | string | `100% of users unable to log in for 47 min` |

## Out-of-corpus questions (deliberate failure mode)

The assistant should **refuse** with the **Not in knowledge base** amber card for questions like:

- "What's the best pasta recipe?"
- "Who won the World Cup in 2022?"
- "How do I install Photoshop?"

This is the grounded-RAG safety property — no hallucination when the KB has no relevant content.
