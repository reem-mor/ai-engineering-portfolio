# Knowledge Base Corpus — Incident Operations

These documents form the source corpus for the Bedrock Knowledge Base.
They are written as NOC / SRE wiki content — concrete commands, thresholds, and named services — so the KB returns grounded answers.

## Demo-focused runbooks (course Q&A)

| File | Sample question |
|---|---|
| `runbook_db_cpu.md` | Postgres CPU is 95% on prod-db-1 — what is the runbook? |
| `runbook_checkout_5xx.md` | API 5xx rate is above 2% on checkout — what should I check? |
| `runbook_queue_lag.md` | Queue lag is above 30 seconds — what should I do? |
| `runbook_auth_login.md` | Users cannot log in after deployment — what should I check? |
| `tier1_escalation_guide.md` | How do I decide if an alert should be resolved at Tier 1 or escalated? |
| `alerts_last_3mo.json` | Historical alert A-1042 checkout 5xx context |
| `postmortem_2024_07.md` | Checkout outage root cause and timeline |

## Format coverage

| Format | Examples |
|---|---|
| **MD** | Runbooks, monitoring reference, postmortem |
| **TXT** | `api_gateway_5xx_runbook.txt`, `payment_service_latency_runbook.txt` |
| **JSON** | `alerts_last_3mo.json` |
| **CSV** | `incident_history.csv` |
| **DOCX** | `deployment_rollback_sop.docx`, `postmortem_template.docx` |
| **PDF** | `escalation_policy.pdf`, `on_call_handoff_checklist.pdf` |

## Out-of-corpus questions

The Knowledge Base only answers incident-operations questions. Off-topic prompts
(for example *"What is the best restaurant in Tokyo?"*) return a graceful
**Not in knowledge base** response with no hallucination.

## How the corpus was built

Hand-authored demo runbooks live in this directory. Binary formats can be regenerated:

```bash
pip install reportlab python-docx
python scripts/build_corpus.py
```

## S3 sync

Upload to `s3://<bucket>/projects/incident-rag-bedrock/data/sample_documents/` and **Sync** the Bedrock data source after changes.

See also: [`data/demo_qa_expected.md`](../demo_qa_expected.md) for grader expected answer outlines.
