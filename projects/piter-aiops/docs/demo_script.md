# Demo Script

## Setup

1. Open the public demo URL (see `screenshots/deployment_validation.md`) or start Docker locally.
2. Confirm `/health`, `/api/health`, `/api/tools/status`, and `/api/history`.
3. Optional deep check: `GET /api/health?deep=1` when Bedrock is configured.

**Public demo (EC2):** http://ec2-3-235-22-143.compute-1.amazonaws.com:8080/ — use `#live-kb` for Knowledge Base Q&A or the main triage flow.

**Local Docker:**

```powershell
docker compose up --build -d
# http://localhost:8080/
```

## Presenter flow (5–7 minutes)

1. **Context** — PITER = Priority, Investigation, Triage, Escalation, Resolution; grounded in runbooks + operational data.
2. **Knowledge Base question:** `What should I check when users cannot log in after the latest deployment?`
   - Show structured PITER sections, citations from `knowledge_base/`, confidence, and next action.
3. **Alert storm / triage** — Select the P1 betting outage alert (or POST `/api/triage` with the demo alert).
   - Highlight deployment correlation, business impact (UKGC), owner team, similar incidents.
4. **Tools** — Point to tool results: recent deployments, service context, similar incidents, escalation preview (mock/preview only).
5. **Follow-up** — `Based on the previous incident, who should I escalate to?`
   - Show session memory and `/api/history`.
6. **Safety** — Escalation preview does not auto-send SMS/email unless explicitly configured for live dispatch.
7. **Closing** — Works with Bedrock Agent + KB on AWS; falls back to local TF-IDF when Bedrock is unavailable.

## Sample incident analysis payload

```json
{
  "alert_title": "High error rate on auth-service",
  "service": "auth-service",
  "environment": "production",
  "severity": "high",
  "description": "Many users cannot log in after the latest production deployment."
}
```

POST to `/api/incidents/analyze` or use the SPA triage panel.

## Pre-demo checklist

```powershell
py -3.12 scripts/verify_credentials.py
py -3.12 scripts/agent_smoke_test.py
py -3.12 scripts/verify_live_demo.py --base-url http://<public-dns>:8080
```
