# PITER AiOps — Dataset Audit

Read-only audit · 2026-06-06

## Dataset inventory

| Dataset | Path | Schema / role |
|---------|------|----------------|
| Workflow alerts | `app/data/workflow_alerts.json` | 6 alerts; drives legacy workflow UI |
| Example questions | `app/data/example_questions.json` | 5 demo prompts |
| Eval questions | `evaluation/test_questions.json` | 7 cases with expected grounding |
| Incident history | `data/sample_documents/incident_history.csv` | 30 rows; 7 columns |
| Alerts history | `data/sample_documents/alerts_last_3mo.json` | JSON alert log |
| Service catalog | `action_groups/iiq-*/data/service_catalog.json` | Per-Lambda copy |
| Deployments | `action_groups/iiq-correlate/data/deploys.csv` | Deploy correlation |
| Impact matrix | `action_groups/iiq-context/data/impact_matrix.csv` | Business impact scoring |
| Demo correlate event | `action_groups/iiq-correlate/events/demo_correlate.json` | Lambda test fixture |

App-layer tools also read from `data/sample_documents/incident_history.csv` via `app/enrichment_tools.py` and `app/services/data_access.py`.

## Schema / quality checks

| Check | Result |
|-------|--------|
| Unique IDs in workflow alerts | **Pass** — `test_workflow_alerts_have_required_fields` |
| Unique eval question IDs | **Pass** — `test_evaluation_questions_schema` |
| Demo corpus files exist | **Pass** — 11 required files + extended corpus |
| Service name consistency | **Good** — `postgres`, `checkout-api`, `auth-api`, etc. |
| Priority values | P1–P4 in CSV and alerts |
| Encoding | UTF-8 (tests read successfully) |
| Malformed JSON | **None found** in committed eval/workflow files |
| Sensitive values | **None** in committed datasets (grep AKIA/password) |

## Memory / follow-up coverage in data

| Scenario | Supported? |
|----------|------------|
| Follow-up owner question | Session memory + owner tool output (`test_follow_up_owner_uses_memory`) |
| Follow-up deploy question | Memory from correlate tool |
| Fresh RAG on SQL/general | Re-query path (`memory_used=false`) |
| Cross-incident isolation | New `session_id` per triage (`session_memory.create_session`) |

## Recommended evaluation set additions (no new data invented)

| Case type | Suggestion |
|-----------|------------|
| Tool-required only | "Who is on-call for postgres?" — expect tool fields, not KB hallucination |
| Multi-document reasoning | "Compare checkout 5xx postmortem to current alert" |
| Missing evidence | "Who owns the fictional-service-x?" — expect unknown/error from tools |
| Noise / refusal | Already have Tokyo restaurant (id 6) |
| Agent path | Add agent-only smoke row when `RAG_BACKEND=agent` stable |

## Gap

`evaluation/test_questions.json` has only 7 rows — adequate for smoke, thin for grading rubric "high-quality evaluation set." Expand using existing corpus only (no fabricated ops facts).
