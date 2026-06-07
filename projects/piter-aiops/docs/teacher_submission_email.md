# Submission email — Mid-course project (Milestone 1)

> Copy the block below into your mail client. Replace `[Teacher name]` and `[Teacher email]`
> before sending. All dataset and Q&A facts below are verified artifacts in this repo.

---

**To:** [Teacher email]  
**From:** Re'em Mor <[your-email]>  
**Subject:** Mid-course project (Milestone 1) — PITER AiOps Bedrock RAG: repo, dataset, and sample Q&A

Hi [Teacher name],

Thank you for the chat on Friday and for approving the idea. As we discussed, here is **Milestone 1** of my mid-course project — **PITER AiOps · Bedrock RAG**, a topic-based RAG web app for incident operations (Amazon Bedrock Knowledge Base + Flask + Docker + EC2). It answers **only from my own document corpus, cites the source for every answer, and refuses instead of hallucinating** when a question is out of scope.

**Repository:** https://github.com/reem-mor/amdocs-ai-course/tree/main/projects/incident-rag-bedrock  
(README has full run/deploy instructions, architecture, and the component breakdown.)

---

## 1. Dataset (topic: NOC / DevOps / SRE incident operations)

A small, focused corpus of **10 synthetic documents across all 5 Bedrock S3 formats** — MD (3), TXT (2), CSV (1), DOCX (2), PDF (2). It is hand-authored and fully reproducible (`python scripts/build_corpus.py`), with **no real customer data, PII, or secrets**.

Full dataset card: `data/sample_documents/README.md`

| Format | Count | Files |
|--------|-------|-------|
| **MD** | 3 | `auth_service_runbook.md`, `database_connectivity_runbook.md`, `monitoring_alerts_reference.md` |
| **TXT** | 2 | `api_gateway_5xx_runbook.txt`, `payment_service_latency_runbook.txt` |
| **CSV** | 1 | `incident_history.csv` (30 rows of past incidents) |
| **DOCX** | 2 | `deployment_rollback_sop.docx`, `postmortem_template.docx` |
| **PDF** | 2 | `escalation_policy.pdf`, `on_call_handoff_checklist.pdf` |

**Where it lives:**
- In the repo: `projects/incident-rag-bedrock/data/sample_documents/`
- In AWS (KB data source): `s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/`

---

## 2. Sample questions & answers (live Bedrock results)

Captured by `scripts/kb_smoke_test.py`; full transcript in `evaluation/qa_showcase.md`.

| # | Question | Result | Source |
|---|----------|--------|--------|
| 1 | How do I triage an authentication service incident? | Grounded | `auth_service_runbook.md` |
| 2 | Which runbook should I follow for database connectivity issues? | Grounded | `database_connectivity_runbook.md` |
| 3 | What are the escalation steps for a P1 production outage? | Grounded | `escalation_policy.pdf` |
| 4 | What should I check first when users cannot log in after a deployment? | Grounded | `auth_service_runbook.md` |
| 5 | What is the best restaurant in Tokyo? *(off-topic)* | Refusal — **Not in knowledge base**, no hallucination | — |
| 6 | `what is the` *(invalid input)* | Rejected by validation before any model call | — |

Smoke suite: **6/6 PASS** (`evaluation/smoke_results.md`).

---

## 3. Tests & verification (best practice as per your requirements)

- **`pytest`** — offline unit/data tests, **no live AWS calls** (Stubber + fakes)
- **`python scripts/kb_smoke_test.py`** — live Bedrock KB, 6/6
- **`scripts/verify_e2e.py`** + **`/health`** against the running container
- Runs in **Docker** with **gunicorn** (not the Flask dev server), **non-root** container, healthcheck
- Deployed to **EC2 t3.micro** using an **IAM instance profile** — no AWS keys on disk; SSH locked to my IP; CSRF + server-side validation on all inputs

---

## 4. Screenshots (proof)

In `screenshots/` — Bedrock KB + synced data source, model access, EC2 instance + security group, `docker ps` healthy, the public app, grounded answer with citations, the off-topic refusal, `pytest` passing, the 6/6 smoke run, the dataset corpus, and a live Q&A showcase.

Key files for grading (Tier 1):
- `01_bedrock_kb_overview.png` · `02_bedrock_kb_data_source_synced.png` · `03_bedrock_model_access_granted.png`
- `04_ec2_instance_running.png` · `05_security_group_rules.png` · `06_docker_ps_on_ec2.png`
- `07_app_homepage_public.png` · `08_app_question_and_answer.png` · `08b_app_citations_expanded.png` · `09_app_refusal_or_low_confidence.png`
- `10_cleanup_console.png`

Optional depth: `11`–`19` in `screenshots/` (see `screenshots/README.md`).

---

## 5. Where this is going (next milestone)

Milestone 1 is the grounded-RAG foundation. Next, I want to grow it into a **production enterprise incident console** for NOC / DevOps / SRE teams: real-time prioritization of alerts by **business impact and money-at-risk**, learning incident **patterns** over time, searching the **company knowledge base**, and correlating each alert with **recent deployments/version uploads, the owning vertical, host owners, and analytics metrics** — using MCP/tools and agents on top of this same Bedrock retrieve-and-cite core.

Happy to give a short live demo whenever convenient.

Best regards,  
**Re'em Mor**  
[your-email] · GitHub: @reem-mor
