# Code review — PITER AiOps (`projects/piter-aiops`)

Final self-review for course submission: datasets, corpus, KB sync, Flask API, React SPA, and AWS integration.

> Historical note: earlier milestones used the repo path `projects/incident-rag-bedrock` and the working title IncidentIQ. Product branding is **PITER AiOps**; S3/KB corpus prefix is `projects/piter-aiops/`.

## Verdict

**Ready for top-grade submission** when live checks pass: offline pytest green, corpus on disk, KB smoke 6/6, `verify_live_demo.py` 29/29, SPA E2E with Docker.

## Strengths

- **Separation of concerns:** `upload_validators.py`, `upload_service.py`, `bedrock_client.py`, `routes.py` (HTTP only), `data_loader.py` (examples + corpus metadata).
- **Consistent error model:** `BedrockError` with stable `code` values; boto3 mapped in `errors.py`.
- **Testability:** 270+ pytest tests with Stubber/fakes; upload routes use injectable fakes; SPA covered in `tests/test_spa_mode.py`; corpus alignment in `tests/test_data_corpus.py`.
- **Security:** `secure_filename`, suffix whitelist, size cap, scoped IAM; CSRF enabled with `main_bp` exempt for JSON SPA (token still from `/api/bootstrap`).
- **KB sync UX:** S3 success + ingestion failure returns **HTTP 202** (`partial`, `sync_warning`) instead of losing the upload outcome.
- **Follow-ups:** `session_id` passed through `/ask` to Bedrock for multi-turn Q&A in the SPA.
- **Data quality:** `evaluation/test_questions.json` and `example_questions.json` grounded in corpus stems; off-topic refusal tested.

## Corpus and datasets

| Asset | Count / status |
|-------|----------------|
| `data/sample_documents/` | **10** documents + README (within 5–15 guideline) |
| Example questions (UI) | `app/data/example_questions.json` with grouped labels |
| Eval / smoke | `evaluation/test_questions.json` — 6 cases for `kb_smoke_test.py` |
| Workflow demo | `app/data/workflow_alerts.json` |

Regenerate corpus artifacts if needed: `python scripts/build_corpus.py` (see `data/sample_documents/README.md`).

## Risks / notes (acceptable for course MVP)

| Item | Severity | Notes |
|------|----------|-------|
| SPA vs legacy in pytest | Info | Default `FORCE_LEGACY_UI=True` in `tests/conftest.py`; SPA has dedicated tests |
| Orphan frontend files | Info | `frontend/src/routes/index.tsx`, `rag.functions.ts` not in production bundle |
| Screenshot #11 | Info | May still show older pytest count until re-captured with `capture_screenshots.mjs --pytest-only` |
| Live AWS cost | Info | Run `kb_smoke_test.py` only when creds configured; delete EC2 after demo |

## Verification performed

| Check | Result |
|-------|--------|
| `pytest -q` | **271 passed** (2026-06-08) |
| `npm run build` | SPA → `app/static/spa/` |
| `scripts/kb_smoke_test.py` | **6/6** PASS |
| `scripts/verify_e2e.py` (SPA, `APP_URL=http://127.0.0.1:8080`) | **20/20** PASS |
| KB data source prefix | `projects/piter-aiops/data/sample_documents/` |

Windows: run from project root — `.\scripts\verify.ps1` (not from `frontend/`; venv is at repo root).

## Guideline mapping

See [`GRADING_CHECKLIST.md`](GRADING_CHECKLIST.md). Entry points: [`app.py`](../app.py) (alias), [`wsgi.py`](../wsgi.py) (Gunicorn/Docker).

Edge cases: [`edge_cases.md`](edge_cases.md). Phased review log: [`PRODUCTION_REVIEW.md`](PRODUCTION_REVIEW.md).
