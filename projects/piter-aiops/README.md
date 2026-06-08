# PITER AiOps

PITER AiOps is an AI-powered incident response assistant for NOC, DevOps, SRE, and production operations teams.

PITER stands for:

- Priority
- Investigation
- Triage
- Escalation
- Resolution

## What It Demonstrates

- Flask backend
- React frontend
- Amazon Bedrock Agent integration with `boto3`
- Bedrock Knowledge Base RAG
- MCP-style local tools
- Action Group / Lambda-style tool contracts
- Pandas, CSV, and JSON data processing
- Chat memory and chat history
- Docker
- Tests
- Demo-ready documentation

## Core API

- `GET /health`
- `GET /api/health`
- `POST /api/chat`
- `POST /api/incidents/analyze`
- `GET /api/history`
- `DELETE /api/history`
- `GET /api/tools/status`

## Run Locally

```powershell
python -m pytest
cd frontend
npm run build
cd ..
docker compose up --build
```

Smoke checks:

```powershell
Invoke-RestMethod http://localhost:8080/health
Invoke-RestMethod http://localhost:8080/api/health
Invoke-RestMethod http://localhost:8080/api/tools/status
Invoke-RestMethod http://localhost:8080/api/history
```

## Knowledge Base

The authoritative RAG corpus is `knowledge_base/`.

Recommended S3 prefix:

```text
s3://<bucket-name>/projects/piter-aiops/knowledge_base/
```

Sync:

```powershell
aws s3 sync knowledge_base/ s3://<bucket-name>/projects/piter-aiops/knowledge_base/
```

## Data

Top-level demo data:

- `data/deployments.csv`
- `data/historical_incidents.csv`
- `data/services.json`
- `data/escalation_rules.json`
- `data/demo_questions.json`
- `data/tool_test_cases.json`
- `data/sample_alerts.json`

Runtime compatibility datasets remain under `data/source/`, `data/agent_data/`, and `data/sample_documents/incident_history.csv`.

Validate:

```powershell
python scripts/validate_data.py
```

## MCP Tools

Core local tool registry:

- `get_recent_deployments`
- `get_service_context`
- `find_similar_incidents`
- `get_escalation_recommendation`

Run:

```powershell
python mcp/server.py --selftest
```

## AWS Setup

See `docs/aws_sync_guide.md` and `infra/`.

Required environment placeholders are in `.env.example`.

## Demo Question

```text
What should I check when users cannot log in after the latest deployment?
```

Expected response includes structured PITER fields, business impact, next action, sources, tool results, and memory.
