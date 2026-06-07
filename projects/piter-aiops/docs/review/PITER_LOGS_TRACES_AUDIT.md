# PITER AiOps — Logs & Traces Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Logging
- Standard `logging` across 13 modules (`app/**`).
- Bedrock failures logged then degraded: `"Bedrock failed (…) — answering from LOCAL knowledge base"`.
- Notification logs **mask** phone numbers (`{phone[:4]}***{phone[-2:]}`).
- No secrets, tokens, or raw recipients logged.

## Tracing
- `invoke_agent` called with `enableTrace=True` → Bedrock returns reasoning/tool/KB trace events,
  parsed in `app/bedrock_agent_client.py`. Documented for CloudWatch inspection.

## Checklist
| Item | Status | Note |
| ---- | ------ | ---- |
| Request/correlation ID | PARTIAL | session_id present; no dedicated request-id middleware |
| Incident ID in logs | PARTIAL | present in notification/escalation paths |
| Session ID in logs | PARTIAL | available; not logged on every path |
| Tool-call logs | PASS | enrichment/escalation paths |
| Fallback mode logs | PASS | explicit warning on Bedrock→local |
| Bedrock errors sanitized | PASS | `app/errors.py` translates to safe messages |
| No secrets in logs | PASS | — |
| No raw phone/email in logs | PASS | masked |
| CloudWatch log group docs | PARTIAL | referenced in deploy docs |
| Local logs safe | PASS | — |
| Trace parsing documented | PASS | `enableTrace` + parser |

## Recommendations (non-blocking)
- Add a lightweight `before_request` correlation-id (uuid) and include `incident_id`/`session_id`
  consistently in structured log lines for end-to-end traceability.

## Status: PARTIAL — safe and useful; correlation-id coverage can be tightened.
