# Screenshots

Submission proof captures for **Incident RAG Bedrock**. PNGs use the exact filenames below.

## What to submit (Tier 1)

Attach these **11 files** from the repo root `screenshots/` folder for course grading:

| # | File | Proof |
|---|------|-------|
| 01 | `01_bedrock_kb_overview.png` | KB `RBTJM6NIG9` active |
| 02 | `02_bedrock_kb_data_source_synced.png` | Data source **Available** |
| 03 | `03_bedrock_model_access_granted.png` | Nova / model access |
| 04 | `04_ec2_instance_running.png` | `i-05cbc9f5604d6704e` running (historical; instance terminated) |
| 05 | `05_security_group_rules.png` | **8080/tcp** from `0.0.0.0/0` |
| 06 | `06_docker_ps_on_ec2.png` | Container healthy on port 8080 |
| 07 | `07_app_homepage_public.png` | Full app homepage |
| 08 | `08_app_question_and_answer.png` | Grounded answer — numbered steps + SQL blocks |
| 08b | `08b_app_citations_expanded.png` | Same answer, citations expanded (visual cards) |
| 09 | `09_app_refusal_or_low_confidence.png` | Off-topic refusal only |
| 10 | `10_cleanup_console.png` | Post-teardown console |

> **Note:** `04`–`06` are historical EC2 proof. `07`–`08b` were captured against the same Docker image as ECR `:demo` (localhost or public IP).

## Tier 2 — README / instructor depth

Optional depth for reviewers; regenerate with `capture_screenshots.mjs` where noted.

| File | Shows |
|------|-------|
| `11_pytest_passed.png` | `pytest -v` — full unit suite passing |
| `12_kb_smoke_evaluation.png` | `evaluation/smoke_results.md` rendered — **6/6 PASS** |
| `13_mvp_workflow.png` | `#mvp` after **Run triage** — numbered steps + citation cards in triage panel |
| `14_architecture.png` | `#architecture` with Documents block selected |
| `15_document_upload_success.png` | Upload success + S3 key |
| `16_document_upload_validation.png` | Client validation — missing file |
| `17_document_upload_type_rejected.png` | Unsupported type rejected |
| `18_dataset_corpus.png` | 10-document corpus catalog |
| `19_sample_questions_answers.png` | `evaluation/qa_showcase.md` — 4 grounded + 1 refusal |

```powershell
cd scripts
node capture_screenshots.mjs --mvp-only   # refresh 13 only
node capture_screenshots.mjs --pytest-only
```

## Tier 3 — Extras (`extras/`)

Responsive Part A crops — grader-optional; not in the Tier 1 zip.

| File | Shows |
|------|-------|
| `extras/partA_answer_1440.png` | Live KB answer panel @ 1440px |
| `extras/partA_answer_expanded_1440.png` | Citations expanded @ 1440px |
| `extras/partA_answer_768.png` | Tablet crop |
| `extras/partA_answer_390.png` | Mobile crop |

```powershell
cd scripts
node capture_partA.mjs   # writes to screenshots/extras/
```

## Archive (`archive/`)

Not for submission — kept for audit only.

| File | Reason |
|------|--------|
| `archive/partA_home_1440.png` | Duplicate of `07_app_homepage_public.png` |
| `archive/20_codex_local_verification.png` | Redundant with `11` + `19` |

## Course submission name map

If your grader expects hyphenated filenames, rename or copy from the Tier 1 set:

| Course name | Repo filename |
|-------------|---------------|
| `01-bedrock-knowledge-base.png` | `01_bedrock_kb_overview.png` |
| `02-bedrock-data-source-sync.png` | `02_bedrock_kb_data_source_synced.png` |
| `03-flask-local-app.png` | `07_app_homepage_public.png` |
| `04-successful-question-answer.png` | `08_app_question_and_answer.png` |
| `05-docker-container-running.png` | `06_docker_ps_on_ec2.png` |
| `06-ec2-instance-details.png` | `04_ec2_instance_running.png` |
| `07-public-ec2-app.png` | `07_app_homepage_public.png` |
| `08-cleanup-proof.png` | `10_cleanup_console.png` |

## Automated captures (regenerate locally)

Prerequisites: Docker running, `.env` with valid `BEDROCK_KB_ID` and inference profile ARN, app on `http://localhost:8080`.

```powershell
cd projects/incident-rag-bedrock

docker compose up --build -d
Invoke-WebRequest http://localhost:8080/health   # {"status":"ok"}

py -3.12 scripts/kb_smoke_test.py
# → evaluation/smoke_results.md, evaluation/qa_showcase.md

cd scripts
npm install
npx playwright install chromium
node capture_screenshots.mjs          # 07–09 (legacy HTMX paths), 11–19
node capture_screenshots.mjs --mvp-only
node capture_screenshots.mjs --pytest-only

$env:APP_URL="http://<public-ip>:8080"
node capture_public_app.mjs           # 07 (if not localhost), 08, 08b

node capture_partA.mjs                # extras/partA_*
node capture_aws_proof.mjs            # 01–03
node capture_ec2_proof.mjs            # 04–06 (while instance running)
node capture_cleanup_proof.mjs        # 10 after terminate
```

| Output file | Capture method |
|-------------|----------------|
| `07_app_homepage_public.png` | `capture_public_app.mjs` or `capture_screenshots.mjs` |
| `08_app_question_and_answer.png` | Grounded SQL question → numbered steps + code blocks |
| `08b_app_citations_expanded.png` | Same answer, **Retrieved citations** expanded |
| `09_app_refusal_or_low_confidence.png` | Off-topic → refusal / no-match |
| `11_pytest_passed.png` | Rendered pytest output |
| `12_kb_smoke_evaluation.png` | Rendered `evaluation/smoke_results.md` |
| `13_mvp_workflow.png` | `#mvp` after **Run triage** (SPA; use `--mvp-only` to refresh) |
| `14_architecture.png` | `#architecture` — Documents selected |
| `15`–`17` | Document upload flows |
| `18_dataset_corpus.png` | Corpus catalog from `data/sample_documents/README.md` |
| `19_sample_questions_answers.png` | `evaluation/qa_showcase.md` |

## Manual captures (AWS Console / EC2)

| # | Filename | What it must show |
|---|---|---|
| 01 | `01_bedrock_kb_overview.png` | Bedrock → Knowledge bases → `RBTJM6NIG9` |
| 02 | `02_bedrock_kb_data_source_synced.png` | Data source **Status: Available** |
| 03 | `03_bedrock_model_access_granted.png` | Model access enabled |
| 04 | `04_ec2_instance_running.png` | EC2 instance running with public IP |
| 05 | `05_security_group_rules.png` | Inbound **8080/tcp** from `0.0.0.0/0` |
| 06 | `06_docker_ps_on_ec2.png` | `docker ps` → `Up (healthy)` on 8080 |
| 10 | `10_cleanup_console.png` | Empty console after teardown |

See [`deployment_validation.md`](deployment_validation.md) for the latest validation log.
