# PITER Logs & Traces Audit

## Local logging

| Area | Pattern |
|------|---------|
| Bedrock failures | `log.exception` in `bedrock_client.py` — sanitized via `BedrockError` |
| Fallback | `WARNING Bedrock failed — answering from LOCAL` in `routes.py` |
| Lambda | JSON event log once per invoke |
| Request IDs | Not consistently propagated to JSON responses |

## Correlation

| ID | Present in triage response | In logs |
|----|---------------------------|---------|
| session_id | Yes | Partial |
| incident/alert id | In alert payload | Partial |
| ingestion_job_id | Upload response | Yes |

## CloudWatch

Not queried in depth this session (read-only optional). Lambda log groups expected: `/aws/lambda/iiq-*`.

## Trace parsing

`bedrock_agent_client.py` parses invocation traces for citations — documented in code comments.

## Gaps

1. Add `request_id` middleware (Flask `g.request_id`)
2. Structured JSON logging option for demo troubleshooting
3. Document CloudWatch log group names in `docs/aws_setup.md`

## Error sanitization

User-facing errors use `BedrockError.user_message` — avoids raw boto3 traces in API JSON.
