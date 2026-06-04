# IncidentIQ Mid-Project — Submission Checklist

Requirements map (master prompt R1–R11) to repo evidence. Deploy/screenshots completed — see [`DEPLOY_STATUS.md`](DEPLOY_STATUS.md).

## Requirements coverage

| # | Requirement | Evidence |
|---|-------------|----------|
| R1 | RAG over documents | KB `RBTJM6NIG9` + `data/sample_documents/` |
| R2 | KB connected to agent | Agent `HH4YGSLZUE` + [`docs/bedrock_agent_setup.md`](bedrock_agent_setup.md) |
| R3 | 2–4 Lambda functions | `iiq-correlate`, `iiq-context`, `iiq-similar` (+ optional `incidentiq-actions`) |
| R4 | CSV/JSON + Pandas | [`app/enrichment_tools.py`](../app/enrichment_tools.py), [`data/agent_data/`](../data/agent_data/) |
| R5 | MCP manages Lambdas | Path B: action groups — [`docs/MCP_PATH.md`](MCP_PATH.md) |
| R6 | Session memory + follow-ups | [`app/bedrock_agent_client.py`](../app/bedrock_agent_client.py), SPA follow-up box |
| R7 | System prompt | `AGENT_INSTRUCTION` in `bedrock_agent_client.py` |
| R8 | Flask app | [`app/routes.py`](../app/routes.py), `POST /api/workflow/triage` |
| R9 | Docker | [`Dockerfile`](../Dockerfile), [`docker-compose.yml`](../docker-compose.yml) |
| R10 | Tests / edge cases | `pytest` under [`tests/`](../tests/) |
| R11 | README + clean repo | [`README.md`](../README.md), `.env.example`, no secrets committed |

## Local verification commands

```powershell
cd projects\incidentIQ-midproject

# Python unit tests (offline)
.\.venv\Scripts\python.exe -m pytest -q

# Frontend production bundle
cd frontend
npm ci
npm run build
cd ..

# Docker smoke (no push)
docker compose build

# Optional live checks (read-only / smoke — needs AWS creds)
$env:AWS_PROFILE="reemmor"
$env:AWS_REGION="us-east-1"
python scripts\kb_smoke_test.py
python scripts\agent_smoke_test.py
```

## Environment variables

Copy [`.env.example`](../.env.example) → `.env`. Required for agent mode:

- `BEDROCK_KB_ID`, `BEDROCK_AGENT_ID`, `BEDROCK_AGENT_ALIAS_ID`
- `BEDROCK_MODEL_ARN`, `AWS_REGION`, `FLASK_SECRET_KEY`
- `RAG_BACKEND=agent`

Do **not** commit `.env` or paste API keys into the repo.

## Screenshot set (agent architecture — prompt #3)

Capture into [`screenshots/`](../screenshots/) when approved for live deploy:

| File | Proof |
|------|-------|
| `01_agent.png` | Bedrock Agent + alias, KB associated |
| `02_kb_sync.png` | KB data source synced |
| `03_mcp.png` | Action groups (or Gateway if Path A) |
| `04_lambdas.png` | `iiq-*` Lambda functions |
| `05_s3.png` | S3 runbook prefix |
| `06_ec2.png` | EC2 instance + SG |
| `07_app_home.png` | App homepage |
| `08_qa.png` | Postgres CPU triage card |
| `09_memory_followup.png` | Follow-up in same session |
| `10_mobile.png` | 390px triage card |
| `11_docker_ps.png` | `docker ps` healthy |
| `12_tests.png` | `pytest` green |

Legacy Tier-1 filenames (`01_bedrock_kb_overview.png`, etc.) remain valid for earlier grading maps — see [`screenshots/README.md`](../screenshots/README.md).

## Optional follow-ups

- KB **sync** after new documents
- Lambda **redeploy** / agent prepare
- AgentCore Gateway + Cognito (Path A)
- Post-demo **teardown** — [`docs/TEARDOWN.md`](TEARDOWN.md) (instance `i-016d77ef747791213` is running until you terminate it)

## Downloads runbooks (not integrated)

Control sheet references `RB-001`…`RB-006` under `kb_documents/`. This repo uses equivalent runbooks in `data/sample_documents/` (`runbook_db_cpu.md`, `runbook_connection_pool.md`, etc.). Upload/sync to S3 is a separate, approved step.
