# Troubleshooting

## Empty User Message

`/api/chat` returns `empty_question` with a safe message.

## Unknown Service

Tools return structured `error` fields instead of crashing the backend.

## Missing Data File

Run:

```powershell
python scripts/validate_data.py
```

The script reports the missing CSV/JSON file or column.

## Bedrock Unavailable

Set `PITER_USE_BEDROCK=false` for local fallback, or keep fallback enabled while testing Bedrock.

## Missing Agent IDs

For `RAG_BACKEND=agent`, configure:

- `BEDROCK_AGENT_ID`
- `BEDROCK_AGENT_ALIAS_ID`

## Knowledge Base Not Synced

Sync `knowledge_base/` to S3, start ingestion, and test retrieval before the live demo.

## History

- `GET /api/history` returns the current process-local history.
- `DELETE /api/history` clears history.
- History resets when the Flask process restarts.
