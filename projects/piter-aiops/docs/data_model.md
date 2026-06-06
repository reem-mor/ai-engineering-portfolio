# Data model

## Canonical folders

| Path | Purpose |
|---|---|
| `data/source/` | Generator output — deterministic demo datasets (alert storm, incidents, deploys) |
| `data/agent_data/` | Runtime enrichment inputs (fallback when source schemas differ) |
| `data/sample_documents/` | RAG corpus for local fallback and Bedrock S3 sync |
| `knowledge_base/` | Structured mirror with YAML front matter for docs and manifest API |

## Alert stream (`data/source/alert_stream.csv`)

- **399 data rows** (generator target 400; header excluded)
- One deterministic P1 trigger: `ALT-DEMO-P1-001` on `bet-service` / `GIB-UKGC`
- Five warning shots prefixed `ALT-DEMO-WARN-`
- Severity mix drives noise suppression counts in the UI

## Identifiers

- Alerts: `ALT-*` / `ALT-DEMO-*`
- Investigations: `INV-YYYY-MMDD-NNN`
- Deployments: `DEP-YYYY-MM-DD-NNN`

## Privacy rules

No real phone numbers or personal email addresses in CSV, JSON, KB markdown, tests, or UI examples.

See also: [`knowledge_base.md`](knowledge_base.md), [`live_demo.md`](live_demo.md).
