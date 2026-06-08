# Data Dictionary

## Top-Level Demo Data

- `data/deployments.csv`: recent deployments for demo lookup.
- `data/historical_incidents.csv`: compact incident history for evaluation and demo explanation.
- `data/services.json`: service ownership, dependencies, SLA, and escalation team.
- `data/escalation_rules.json`: priority-based safe escalation rules.
- `data/demo_questions.json`: presenter-facing demo questions.
- `data/tool_test_cases.json`: tool input/output expectations.
- `data/sample_alerts.json`: ready-to-send incident analysis payloads.

## Runtime Compatibility Data

- `data/source/`: deterministic alert stream and structured data used by the Flask incident-analysis pipeline.
- `data/agent_data/`: legacy Postgres demo data still covered by tests.
- `data/sample_documents/incident_history.csv`: legacy incident history used only by the Postgres fallback similarity path.

## Validation

Run:

```powershell
python scripts/validate_data.py
```

CSV files are loaded with Pandas and JSON files are parsed with required key checks.
