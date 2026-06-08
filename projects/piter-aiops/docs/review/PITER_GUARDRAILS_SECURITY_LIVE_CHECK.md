# PITER Guardrails and Security Live Check

**Date:** 2026-06-08

## Layers

| Layer | Status |
|-------|--------|
| App guardrails | `tests/test_guardrails.py` — pass |
| Bedrock Guardrail | `rti921amc6u3` v2 on agent alias |
| Upload safety | Path traversal + type validation |
| Notification masking | No raw phone/email in logs/UI |

## Test prompts (automated + manual policy)

| Prompt class | Expected |
|--------------|----------|
| Prompt injection | Block or safe refusal |
| Secrets extraction | No secrets returned |
| Destructive rollback without confirm | Refusal / policy message |
| Raw phone/email request | Masked or refused |
| Off-topic unsafe | Grounded refusal |

## UI signal

Sidebar: **Guardrails active** — grounded answers only.

## CSRF

API routes CSRF-exempt for demo SPA — documented risk; acceptable for local demo container only.

## Prior report

`PITER_GUARDRAILS_AWS_CHECK.md`
