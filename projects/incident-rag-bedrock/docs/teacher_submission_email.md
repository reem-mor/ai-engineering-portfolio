# Submission email — Dataset + sample Q&A

> Copy the block below into your mail client. Replace `[Teacher name]` and attach or link
> the repo. The dataset and answers referenced here are real, verified artifacts in this
> project — nothing in this email is invented.

---

**To:** [Teacher email]
**From:** Re'em Mor <reem.mor3@gmail.com>
**Subject:** IncidentIQ · Bedrock RAG — dataset and sample questions & answers

Hi [Teacher name],

Thank you for the approval. As requested, here is the **dataset** and a set of **sample
questions and answers** for my project, *IncidentIQ · Bedrock RAG* — a topic-based
Retrieval-Augmented Generation web app (Amazon Bedrock Knowledge Base + Flask + Docker +
EC2). The app answers incident-response questions **only from my own document corpus,
cites the source document for every answer, and refuses (instead of hallucinating) when a
question is outside the corpus.**

---

## 1. The dataset

**Topic:** Incident Operations (NOC / DevOps / SRE) — runbooks, SOPs, escalation policy,
and incident history. It is a small, focused corpus of **10 documents** written to look
like a real on-call wiki (concrete commands, thresholds, and named services), so the
Knowledge Base can return useful, grounded answers.

**Format coverage** — all five formats the Bedrock S3 connector supports:

| Format | Count | Files |
|---|---|---|
| **MD** | 3 | `auth_service_runbook.md`, `database_connectivity_runbook.md`, `monitoring_alerts_reference.md` |
| **TXT** | 2 | `api_gateway_5xx_runbook.txt`, `payment_service_latency_runbook.txt` |
| **CSV** | 1 | `incident_history.csv` (30 rows of past incidents) |
| **DOCX** | 2 | `deployment_rollback_sop.docx`, `postmortem_template.docx` |
| **PDF** | 2 | `escalation_policy.pdf`, `on_call_handoff_checklist.pdf` |

**What each document lets the assistant answer:**

| Document | Sample question it covers |
|---|---|
| `auth_service_runbook.md` | How do I triage an authentication service incident? |
| `database_connectivity_runbook.md` | What checks do I run when Postgres connections are failing? |
| `monitoring_alerts_reference.md` | What does the `AuthGlobalErrorRateCritical` alert mean and what do I do? |
| `api_gateway_5xx_runbook.txt` | API Gateway is returning 5xx storms — what's the runbook? |
| `payment_service_latency_runbook.txt` | How do I fail over to the backup payment provider? |
| `incident_history.csv` | What was the root cause of INC-2025-022? How many P1s did auth-api cause in 2025? |
| `deployment_rollback_sop.docx` | When should I roll back a deployment vs. roll forward? |
| `postmortem_template.docx` | What sections does a postmortem need? |
| `escalation_policy.pdf` | What's the difference between P1 and P2 severity? |
| `on_call_handoff_checklist.pdf` | What should I do at the start of an on-call shift? |

**Provenance & data hygiene:** the corpus is **synthetic** — I hand-authored it in
`scripts/build_corpus.py`, so it is fully reproducible (`python scripts/build_corpus.py`
regenerates all 10 files). It contains **no real customer data, PII, or secrets**; every
service name, hostname, incident ID, and role is fictional.

**Where it lives:**
- In the repo: `projects/incident-rag-bedrock/data/sample_documents/`
  (with a full dataset card in `data/sample_documents/README.md`)
- In AWS (KB data source):
  `s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/`

---

## 2. Sample questions and answers

These are **live results from the Bedrock Knowledge Base** (captured by
`scripts/kb_smoke_test.py`; full transcript in `evaluation/qa_showcase.md`). Each grounded
answer below was returned with a **citation to the source document** shown.

### Q1. How do I triage an authentication service incident?
**Grounded:** yes · **Source:** `auth_service_runbook.md`

> To triage an authentication service incident:
> 1. **Confirm the scope.** Check the auth dashboard global error rate. If
>    `auth_login_errors_total` is above 5% over the last 5 minutes, declare a P2
>    immediately; above 25% → P1.
> 2. **Check recent deployments.** Run `kubectl -n auth get deploy -o wide`; if the latest
>    rollout is under 30 minutes old, treat the deployment as the likely cause and prepare
>    a rollback.
> 3. **Check upstream dependencies.** Confirm Redis (session store) and Postgres (user
>    table) are healthy in the Service Map before suspecting the auth service itself.
> 4. **Validate the OIDC discovery document.**

### Q2. Which runbook should I follow for database connectivity issues?
**Grounded:** yes · **Source:** `database_connectivity_runbook.md`

> Follow the *Database Connectivity Runbook*. It covers issues such as applications logging
> "connection refused", "too many connections", or "SSL handshake failed", along with
> symptoms like high p95 query latency or replication lag.

### Q3. What are the escalation steps for a P1 production outage?
**Grounded:** yes · **Source:** `escalation_policy.pdf`

> 1. The primary on-call engineer is paged immediately.
> 2. If they don't acknowledge within 8 minutes, the secondary on-call engineer is paged
>    automatically.
> 3. After a further 8 minutes without acknowledgement, the on-call engineering manager is
>    paged.
> 4. The engineering manager is woken for any P1 lasting more than 30 minutes, any incident
>    risking customer data confidentiality/integrity/availability, and any incident
>    involving payment processing.

### Q4. What should I check first when users cannot log in after a deployment?
**Grounded:** yes · **Source:** `auth_service_runbook.md`

> Check recent deployments first. If the latest `auth-api` rollout is less than 30 minutes
> old, treat the deployment as the likely cause and prepare a rollback per the standard
> recovery actions.

### Q5. What is the best restaurant in Tokyo? *(off-topic — safety check)*
**Grounded:** no · **Citations:** 0

> The model cannot find sufficient information to answer this question. The knowledge base
> does not contain information related to restaurants in Tokyo.

*Result: the app shows an amber **"Not in knowledge base"** card and does not hallucinate.*

### Q6. `what is the` *(invalid input — validation check)*

> Rejected before any model call with a clear validation error (`stopwords_only`): the
> query has no meaningful content to search on.

**Summary:** 4 grounded answers (each citing the correct source document) + 1 graceful
refusal on an off-topic question + 1 input-validation rejection. The smoke suite scores
**6/6 PASS** (`evaluation/smoke_results.md`).

---

## 3. How to verify / reproduce

- **Rebuild the dataset:** `python scripts/build_corpus.py`
- **Unit + data tests:** `pytest` (includes `tests/test_data_corpus.py`, which checks the
  corpus and the evaluation questions stay aligned)
- **Re-run the live Q&A against Bedrock:** `python scripts/kb_smoke_test.py` — regenerates
  `evaluation/smoke_results.md` and `evaluation/qa_showcase.md`
- **Proof screenshots:** `screenshots/18_dataset_corpus.png` (the corpus) and
  `screenshots/19_sample_questions_answers.png` (a live Q&A)

Artifacts referenced above:
- Dataset + card — `data/sample_documents/` (`README.md`)
- Evaluation questions — `evaluation/test_questions.json`
- Verified Q&A transcript — `evaluation/qa_showcase.md`
- Smoke results — `evaluation/smoke_results.md`

Happy to walk through a live demo whenever convenient.

Best regards,
**Re'em Mor**
reem.mor3@gmail.com · GitHub: @reem-mor
