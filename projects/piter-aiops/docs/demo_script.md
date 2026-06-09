# Demo script (14 steps)

## Setup

1. Open http://localhost:8080/ or EC2 URL from [`deployment.md`](deployment.md).
2. `GET /api/health` and `/api/bootstrap` return `ok`.
3. Optional: `GET /api/health?deep=1` for `bedrock_agent_configured`, `memory_writable`, `tools_ok`.

## Presenter flow (~5 minutes)

1. **Intro** — PITER = Priority, Investigation, Triage, Escalation, Resolution; grounded in KB + tools.
2. Click **Start Alert Stream** — storm timer and alert count appear in the top bar.
3. Watch alerts populate; noise suppression KPI updates.
4. At **~20s** — P1 modal fires (`ALT-2026-06-10-0251`, bet-service).
5. Click **Analyze Incident** — triage runs; Home shows **P1 analysis** with structured PITER panels.
6. Point to **Priority** and **Business impact** sections.
7. Point to **Investigation** — deployment suspect and similar incidents table (not "N items").
8. Expand **Triage** timeline and **Escalation** policy snippet.
9. Open **Agent Chat** — session matches triage; ask: `What should I check next?`
10. Show follow-up uses `/api/follow-up` (same session_id).
11. Click **Clear** in chat dock — history resets.
12. **History → Past investigations** — open a saved session in chat.
13. **Escalate On-Call** — preview-only unless NOTIFY LIVE badge (configured dispatch).
14. **Close** — hybrid Bedrock when configured; offline KB banner when fallback.

## Pre-class commands

```powershell
aws sts get-caller-identity
cd projects/piter-aiops
py -3.12 -m pytest -q
cd frontend; npm run build; cd ..
py -3.12 scripts/verify_credentials.py
py -3.12 scripts/agent_smoke_test.py
py -3.12 app.py
py -3.12 scripts/verify_live_demo.py --base-url http://<host>:8080
```

## Sample triage payload

```json
{
  "service": "bet-service",
  "environment": "GIB-UKGC",
  "severity": "P1",
  "symptom": "100% error rate on bet placement",
  "alert_time": "2026-06-10T10:02:00Z",
  "alert_id": "ALT-2026-06-10-0251"
}
```

POST `/api/triage`.
