# Demo Script

## Setup

1. Start Docker or the local Flask server.
2. Open the React frontend.
3. Confirm `/health`, `/api/health`, `/api/tools/status`, and `/api/history`.

## Demo Flow

1. Ask: `What should I check when users cannot log in after the latest deployment?`
2. Show the PITER response: Priority, Investigation, Triage, Escalation, Resolution.
3. Point to citations from `knowledge_base/`.
4. Run incident analysis for auth-service:

```json
{
  "alert_title": "High error rate on auth-service",
  "service": "auth-service",
  "environment": "production",
  "severity": "high",
  "description": "Many users cannot log in after the latest production deployment."
}
```

5. Show tool results: deployments, service context, similar incidents, escalation recommendation.
6. Ask a follow-up: `Based on the previous incident, what should I do next?`
7. Show memory/history and safe escalation preview behavior.

## Closing Message

PITER keeps incident response grounded in runbooks, structured operational data, and safe escalation rules while still working offline through local fallback.
