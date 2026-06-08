# PITER Logs, Traces, and Errors Live Check

**Date:** 2026-06-08

## Local

| Source | Finding |
|--------|---------|
| Docker `web` logs | `/health` 200; no credential leaks observed |
| Flask structured logs | INFO level; boto3 credential source logged (profile name only) |
| Browser console (capture) | **0 errors** on legacy console flow |

## AWS (read-only spot check)

- Lambda CloudWatch log groups — retention 14d (prior alignment)
- Agent traces — available when `RAG_BACKEND=agent` and trace enabled
- Bedrock errors → fallback to local KB (`verify_live_demo` Phase B)

## API errors

Structured JSON `{ok: false, message: ...}` on validation failures (upload, escalation, triage).

## Correlation

Session ID on triage/follow-up responses; incident ID in escalation payload.

## Prior report

`PITER_LOGS_TRACES_AWS_CHECK.md`
