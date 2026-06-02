# Grading checklist — course guideline alignment

Maps the course handout **bedrock_kb_flask_project_guideline.docx** (Bedrock KB + Flask + Docker + EC2) to this repository.

## Topic and documents

| Requirement | Evidence |
|-------------|----------|
| Personal topic | **Incident Operations / NOC** — runbooks, escalation, on-call handoff |
| 5–15 meaningful documents | **10 files** in [`data/sample_documents/`](../data/sample_documents/) (MD, TXT, CSV, PDF, DOCX) — see catalog in [`data/sample_documents/README.md`](../data/sample_documents/README.md) |
| Documents synced to KB | S3 prefix `projects/incident-rag-bedrock/data/sample_documents/` — screenshot `screenshots/02_bedrock_kb_data_source_synced.png` |

## Bedrock Knowledge Base

| Requirement | Evidence |
|-------------|----------|
| KB exists | `screenshots/01_bedrock_kb_overview.png`; `BEDROCK_KB_ID` in `.env.example` |
| Data source attached + synced | `screenshots/02_*`; setup steps in [`docs/bedrock_kb_setup.md`](bedrock_kb_setup.md) |
| boto3 query from app | [`app/bedrock_client.py`](../app/bedrock_client.py) — `retrieve_and_generate` |
| Live Q&A proof | `screenshots/08_*`, `08b_*`, `evaluation/qa_showcase.md`, `kb_smoke_test.py` **6/6** |

## Flask application

| Requirement | Evidence |
|-------------|----------|
| Home page, question, submit, answer | React SPA at `/` or legacy Jinja when `FORCE_LEGACY_UI=1` |
| Topic-themed design | NOC/incident palette, alert console, architecture panel — `screenshots/07_*`, `14_*` |
| Entry point `app.py` | [`app.py`](../app.py) aliases `create_app()`; production uses [`wsgi.py`](../wsgi.py) |

## Docker and EC2

| Requirement | Evidence |
|-------------|----------|
| Dockerfile + compose | [`Dockerfile`](../Dockerfile), [`docker-compose.yml`](../docker-compose.yml) |
| Public access | `screenshots/04_*`, `07_*`; URL in README **Deploy to EC2** |
| Container running | `screenshots/06_docker_ps_on_ec2.png` |

## Screenshots and cleanup

| Requirement | Evidence |
|-------------|----------|
| Required AWS + app captures | Tier 1 (11 files) in [`screenshots/README.md`](../screenshots/README.md); Tier 2 optional |
| Successful Q&A screenshot | `08_app_question_and_answer.png`, `08b_app_citations_expanded.png` |
| Cleanup after demo | `screenshots/10_cleanup_console.png`, [`docs/cleanup_checklist.md`](cleanup_checklist.md), [`cleanup_log.md`](../cleanup_log.md) |

## README submission items

| Item | Location |
|------|----------|
| Topic | README intro |
| Documents used | README + `data/sample_documents/README.md` |
| How it works | README architecture + HTTP API |
| Public URL used | README **Deploy to EC2** |
| Deleted resources | README **AWS Resources — Created & Deleted** |

## Automated verification (grader / student)

Run from **project root** (`projects/incident-rag-bedrock`), not `frontend/`:

```powershell
.\scripts\verify.ps1
# Offline only: .\scripts\verify.ps1 -SkipLiveAws -SkipE2e
```

| Command | Expectation |
|---------|-------------|
| `pytest -q` | **102 passed** (no live AWS) |
| `npm run build` | `app/static/spa/` updated |
| `scripts/kb_smoke_test.py` | **6/6** (needs AWS + `.env`) |
| `APP_URL=... python scripts/verify_e2e.py` | **20/20** with app up |

## Stretch goals (beyond minimum)

- Document upload + optional KB sync — `15_*` screenshots; partial sync returns **HTTP 202**
- Follow-up questions via `session_id` on `/ask`
- Workflow triage — `13_mvp_workflow.png` (step pipeline, session impact, citations; **Demo & Dashboard** tour scrolls to `#architecture`)
- Deep health — `GET /health?deep=1`
