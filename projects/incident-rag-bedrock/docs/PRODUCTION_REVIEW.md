# Production readiness review (phased)

Completed as part of the phased verification plan. **API stack: Flask 3** (not FastAPI).

## Part 1 — Offline baseline

| Check | Result |
|-------|--------|
| `pytest -q` | All tests passed (see badge in README after run) |
| `cd frontend && npm run build` | SPA emitted to `app/static/spa/` |

## Part 2 — Backend review summary

| Area | Finding | Remediation |
|------|---------|-------------|
| `/health` | Liveness only by default | `GET /health?deep=1` reports config presence for S3/Bedrock |
| Follow-up Q&A | `session_id` from Bedrock not reused | `POST /ask` accepts `session_id`; SPA stores it for follow-ups |
| Upload + KB sync | 502 after successful S3 put | HTTP **202** with `partial`, `sync_warning`, file metadata |
| CSRF | `main_bp` exempt for JSON SPA | Documented; bootstrap still returns token |
| IAM | Nova Lite ARNs in template | `infra/README.md` — align `BEDROCK_MODEL_ARN` with policy |

## Part 3 — Data / eval corpus

- `app/data/example_questions.json` — unique questions, grouped labels via `grouped_example_questions()`
- `evaluation/test_questions.json` — grounded cases aligned to `data/sample_documents/` stems (automated in `tests/test_data_corpus.py`)

## Part 4 — E2E script

`scripts/verify_e2e.py` auto-detects SPA (`id="root"`) vs legacy (`topnav`). SPA path validates `/api/bootstrap`, JSON `/ask`, `/api/workflow/triage`.

```bash
docker compose up -d --build
APP_URL=http://127.0.0.1:8080 python scripts/verify_e2e.py
```

## Part 5 — Live AWS

Run when credentials and `.env` are configured:

```bash
python scripts/kb_smoke_test.py
docker compose up --build
curl http://127.0.0.1:8080/health?deep=1
```

**Last run (local):**

| Step | Result |
|------|--------|
| `kb_smoke_test.py` | 6/6 PASS |
| `docker compose up --build` | Container healthy |
| `verify_e2e.py` (SPA) | 20/20 PASS |

Checklist: S3 prefix synced to KB, model access granted, EC2 SG allows app port, instance profile matches `infra/iam_policy.json`.

## Part 6 — Frontend QA

| Check | Status |
|-------|--------|
| Single bootstrap fetch | OK (`BootstrapProvider`) |
| Live KB `POST /ask` + citations | OK |
| Example chips by group | OK (`example_groups`) |
| Follow-up via `session_id` | OK + "New conversation" reset |
| Upload multipart + 202 partial message | OK (`api.ts`) |
| Workflow triage without artificial delay | OK (200ms delays removed) |
| Orphan `frontend/src/routes/index.tsx` | Not in production bundle; legacy TanStack Start stub |

## Part 7 — Tests added

- `tests/test_spa_mode.py` — SPA home, bootstrap groups, `session_id`, deep health
- `tests/test_data_corpus.py` — JSON + corpus alignment
- `tests/test_upload_routes.py` — partial sync HTTP 202
