# PITER AiOps — Guardrails & Security Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Application guardrails (`app/guardrails.py`)
`check_operator_guardrails(question)` (called from `validators.py`) blocks, before any model call:
- **Destructive data:** FLUSHALL/FLUSHDB, DROP DATABASE/TABLE, TRUNCATE, mass DELETE, `rm -rf`, wipe.
- **Unsafe failover:** promote replica, failover, take primary offline, disable replication.
- **Security bypass:** disable WAF/MFA, open firewall `0.0.0.0/0`, bypass auth.
- **Mass disruption:** kill all sessions, terminate all, restart all pods, scale to zero.
- **Policy bypass:** skip confirmation, ignore allowlist, send without token, disable guardrail.
- **Audit tamper:** delete incident, purge audit, silence all.

Plus the Bedrock **agent instruction** carries a non-negotiable REFUSE list (see
`PITER_SYSTEM_PROMPT_REVIEW.md`).

## Threat coverage
| Threat | Mitigation | Status |
| ------ | ---------- | ------ |
| Prompt injection | "do NOT emit tool calls/JSON/Action:"; guardrail regex; KB-only grounding | PARTIAL→Good |
| Secrets extraction | no secrets in prompts/data; redaction | PASS |
| Unsafe commands | guardrail block + agent REFUSE | PASS |
| Destructive ops | guardrail block + human sign-off rule | PASS |
| Phone/email leakage | masking + redaction (Commit 2) | PASS (after Commit 2) |
| Unsupported claims | "state Not in knowledge base" | PASS |
| Sensitive uploads | type/size validation, path-traversal block | PASS |
| Malicious/irrelevant input | length/stopword validation | PASS |

## Bedrock Guardrail resource
Env contract documented: `PITER_GUARDRAIL_ENABLED`, `PITER_GUARDRAIL_ID`, `PITER_GUARDRAIL_VERSION`.
The managed Bedrock Guardrail resource is **NOT VERIFIED** here (no creds). UI shows guardrail
status when enabled.

## Secrets / PII status
| Item | Before | Action |
| ---- | ------ | ------ |
| Personal emails (`r***@gmail.com`, `f***@gmail.com`) | committed (9 files) | **Redacted** → placeholders/env (Commit 2) |
| Phone (`+972-***-5754`) | committed (9 files) | **Redacted** → placeholder/env (Commit 2) |
| AWS account id `329597159579` | committed (~20 files) | **Retained** by user decision (identifier, not secret) |
| Bucket `reem-amdocs-ai-artifacts-3331` | committed | **Retained** by user decision |
| `AKIA…` access keys | none | n/a |
| `.env` | gitignored | OK (only `.env.example` tracked) |

Post-Commit-2 verification: a `git grep` for the personal email local-parts and the phone digits
returns empty across all tracked files.

## UI security signals
Execution mode, guardrail status, notification mode, masked recipients, and confirmation
requirements are surfaced (no fake claims).

## Status: PARTIAL (PII) → strong after Commit 2; managed Guardrail NOT VERIFIED (creds).
