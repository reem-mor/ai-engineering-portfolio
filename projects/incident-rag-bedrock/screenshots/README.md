# Screenshots

Submission proof captures for `incident-rag-bedrock`. Drop PNGs alongside this file using the exact filenames below.

## Automated captures (regenerate locally)

Prerequisites: Docker running, `.env` with valid `BEDROCK_KB_ID` and an **inference profile** model ARN, app on `http://localhost:8080`.

```powershell
cd projects/incident-rag-bedrock

# 1. Start app
docker compose up --build -d
Invoke-WebRequest http://localhost:8080/health   # {"status":"ok"}

# 2. Live KB smoke test (5/5)
py -3.12 scripts/kb_smoke_test.py

# 3. Unit tests + UI screenshots
cd scripts
npm install
npx playwright install chromium
node capture_screenshots.mjs

# Pytest screenshot only
node capture_screenshots.mjs --pytest-only
```

| Output file | Capture method |
|-------------|----------------|
| `07_app_homepage_public.png` | Full-page homepage with hero + sticky nav |
| `08_app_question_and_answer.png` | Auth triage question → `.badge-grounded` + `.citation-list` with labels |
| `09_app_refusal_or_low_confidence.png` | Tokyo restaurant question → `.badge-nomatch` |
| `11_pytest_43_passed.png` | Rendered `py -3.12 -m pytest -v` output (58 tests) |
| `12_kb_smoke_evaluation.png` | Rendered `evaluation/smoke_results.md` (5/5 PASS) |
| `13_mvp_workflow.png` | `#mvp` section after **Run triage** → grounded workflow result |
| `14_architecture.png` | `#architecture` with Documents block selected |

## Manual captures (AWS Console / EC2)

| # | Filename | What it must show |
|---|---|---|
| 01 | `01_bedrock_kb_overview.png` | Bedrock → Knowledge bases → detail page for `RBTJM6NIG9` |
| 02 | `02_bedrock_kb_data_source_synced.png` | Data source row with **Status: Available** after Sync |
| 03 | `03_bedrock_model_access_granted.png` | Bedrock → Model access — generation model enabled |
| 04 | `04_ec2_instance_running.png` | EC2 → Instances — public DNS visible |
| 05 | `05_security_group_rules.png` | Inbound: 22/tcp from your IP, 80/tcp from anywhere |
| 06 | `06_docker_ps_on_ec2.png` | SSH session showing `docker ps` → `Up (healthy)` |
| 10 | `10_cleanup_console.png` | Empty Bedrock / EC2 / OpenSearch console after teardown |

CLI-generated proof (when console capture is inconvenient):

```powershell
cd scripts
node capture_aws_proof.mjs       # 01–03 from AWS CLI
node capture_ec2_proof.mjs       # 04–06 while instance is running
node capture_cleanup_proof.mjs   # 10 after terminate
```

See [`deployment_validation.md`](deployment_validation.md) for the latest automated check log.
