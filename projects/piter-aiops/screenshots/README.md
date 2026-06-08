# Screenshots

Submission proof captures for **PITER AiOps Bedrock Agent mid-project**. PNGs use the exact filenames below.

## Agent architecture set (prompt #3 — preferred for mid-project)

Capture when EC2/demo is approved. Files live in `screenshots/`:

| # | File | Proof |
|---|------|-------|
| 1 | `01_agent.png` | Bedrock Agent `HH4YGSLZUE` + alias, KB linked |
| 2 | `02_kb_sync.png` | KB `RBTJM6NIG9` data source **Available** |
| 3 | `03_mcp.png` | Action groups (Path B) or AgentCore Gateway (Path A) |
| 4 | `04_lambdas.png` | `iiq-correlate`, `iiq-context`, `iiq-similar` |
| 5 | `05_s3.png` | S3 runbook prefix under `piter-aiops` |
| 6 | `06_ec2.png` | EC2 public IP + security group |
| 7 | `07_app_home.png` | SPA homepage |
| 8 | `08_qa.png` | Triage card — Postgres CPU scenario |
| 9 | `09_memory_followup.png` | Follow-up in same Bedrock session |
| 10 | `10_mobile.png` | Triage card @ 390px |
| 11 | `11_docker_ps.png` | Container healthy on 8080 |
| 12 | `12_tests.png` | `pytest` all green |

See [`docs/SUBMISSION_CHECKLIST.md`](../docs/SUBMISSION_CHECKLIST.md) for commands and requirement mapping.

## Live class-demo set (`console_demo/`)

Real captures of the `/console` live-demo surface for the class presentation,
generated against the running container in **Bedrock** mode. They map 1:1 to the
15 live-demo validation points. See [`docs/LIVE_DEMO_CHECKLIST.md`](../docs/LIVE_DEMO_CHECKLIST.md).

| # | File | Proof |
|---|------|-------|
| 01 | `console_demo/01_home.png` | `/console` home — empty alert form |
| 02 | `console_demo/02_demo_alert.png` | Demo alert loaded (postgres / NJ-DGE / P2) before submit |
| 03 | `console_demo/03_loading.png` | 3-step agent processing loader mid-flight |
| 04 | `console_demo/04_triage_card.png` | Full triage card — `mode: bedrock`, cited answer, all 4 tools |
| 05 | `console_demo/05_citations.png` | Citations section (runbook + postmortem) |
| 06 | `console_demo/06_owner_escalation.png` | Owner / on-call / escalation chain |
| 07 | `console_demo/07_business_impact.png` | Cost-per-15-min + SLA / regulatory risk |
| 08 | `console_demo/08_similar_incidents.png` | Similar incidents + MTTR |
| 09 | `console_demo/09_followup_memory.png` | Follow-up answer marked **from memory** |
| 10 | `console_demo/10_mobile.png` | Full triage card @ 390px (projector/mobile) |
| 11 | `console_demo/11_pytest.png` | `pytest` — all green (count varies by release; see `evaluation/pytest_output.txt`) |
| 12 | `console_demo/12_smoke_results.png` | `evaluation/live_smoke_summary.md` rendered |

Regenerate (Docker on `:8080`, `.env` with `USE_BEDROCK=true` for the live set;
falls back to local mode automatically if AWS is down):

```powershell
cd projects/piter-aiops
docker compose up --build -d
.\.venv\Scripts\python.exe -m pytest -ra --tb=short -o console_output_style=count *> evaluation\pytest_output.txt
cd scripts
npm ci ; npx playwright install chromium
node capture_console_demo.mjs        # → screenshots/console_demo/01..12
```

## What to submit (Tier 1 — legacy RAG naming)

> Historical: Tier 1 filenames predate the **PITER AiOps** rename (`incident-rag-bedrock` repo path). PNG contents remain valid proof; capture scripts now use `projects/piter-aiops/`.

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
| `13_mvp_workflow.png` | Clipped `#mvp` h2 + alert/triage grid after **Run triage** (excludes footer pills); full-width in root README |
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
cd projects/piter-aiops

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
node capture_public_app.mjs           # 07 viewport + #live-kb element shots for 08, 08b, 09

node capture_partA.mjs                # extras/partA_*
node capture_aws_proof.mjs            # 01–03
node capture_ec2_proof.mjs            # 04–06 (while instance running)
node capture_cleanup_proof.mjs        # 10 after terminate
```

| Output file | Capture method |
|-------------|----------------|
| `07_app_homepage_public.png` | Viewport only (1440×900), not full-page scroll |
| `08_app_question_and_answer.png` | `#live-kb` element — grounded SQL answer |
| `08b_app_citations_expanded.png` | `#live-kb` element — citations expanded |
| `09_app_refusal_or_low_confidence.png` | `#live-kb` element — off-topic, **Low confidence** badge |
| `11_pytest_passed.png` | Rendered pytest output |
| `12_kb_smoke_evaluation.png` | Rendered `evaluation/smoke_results.md` |
| `13_mvp_workflow.png` | Page clip: `#mvp h2` + `div.mt-8.grid` after triage (`--mvp-only`; excludes Catch/Triage/Suggest/Decide pills); README MVP section |
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
