# PLAN - PITER AiOps Final Demo Readiness

Scope: `projects/piter-aiops/`. Keep the app simple, explainable, and safe for a 5-7 minute mid-project demo.

## Completed baseline

- Confirmed `app/` is the Flask backend package and `frontend/` is the React/Vite dashboard source.
- Confirmed Flask serves the built SPA from `app/static/spa/`.
- Confirmed the AWS path uses `boto3` Bedrock Agent Runtime through `app/bedrock_agent_client.py`.
- Confirmed local fallback remains available when AWS credentials, Agent IDs, or Knowledge Base access are unavailable.
- Confirmed four PITER tool contracts exist across local MCP-style logic and Bedrock Action Group handlers.

## Current target flow

```text
NOC / SRE engineer
-> React dashboard
-> Flask API
-> boto3 Bedrock Agent Runtime invoke_agent
-> Bedrock Agent + Knowledge Base
-> Action Group / MCP-style enrichment tools
-> Structured PITER response
-> Session memory and chat history
-> Dashboard display
```

## Final API contract

- `GET /api/health`
- `POST /api/chat`
- `POST /api/incidents/analyze`
- `POST /api/triage`
- `POST /api/follow-up`
- `GET /api/sessions/<session_id>/history`

Legacy-compatible routes such as `/health`, `/ask`, and `/console` remain available for Docker health checks and older demo flows.

## Demo script

Use [`docs/demo_script.md`](docs/demo_script.md) as the final presenter path:

1. Open dashboard.
2. Run alert storm or incident analysis.
3. Show Bedrock Agent/Knowledge Base grounding.
4. Show tool results.
5. Ask an escalation follow-up.
6. Show memory/history.
7. Close with Settings/Architecture and explain safe fallback.

## Validation checklist

- `python -m pytest -q`
- `cd frontend && npm run build`
- `cd frontend && npm run lint`
- `python scripts/verify_credentials.py`
- `python scripts/agent_smoke_test.py`
- `python scripts/verify_live_demo.py`
- `docker compose build --pull=false`
- `docker compose up -d`
- Smoke test `/api/bootstrap`, `/api/health`, `/api/incidents/analyze`, `/api/chat`, and `/api/sessions/<session_id>/history`.

## Manual AWS requirements

- Keep real AWS credentials outside the repo in the AWS CLI profile.
- Keep `.env` uncommitted.
- Bedrock Agent must be prepared after Agent/action group changes.
- Knowledge Base data source must be synced after corpus changes.
- Live notification dispatch remains gated and mock/preview by default.
