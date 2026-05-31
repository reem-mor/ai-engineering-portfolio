# Knowledge Base Corpus — Incident Operations

These 10 documents form the source corpus for the Bedrock Knowledge Base.
They are deliberately written as if they came from a real NOC / SRE wiki — concrete commands, specific thresholds, named services — so the KB can return useful, grounded answers.

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

## Out-of-corpus questions (deliberate failure mode)

The assistant should **refuse** with the "No matching context" amber card for questions like:

- "What's the best pasta recipe?"
- "Who won the World Cup in 2022?"
- "How do I install Photoshop?"

This is the grounded-RAG safety property — no hallucination when the KB has no relevant content.
