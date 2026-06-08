# PITER AWS Phase 8 — Guardrails Verification

**Audit date:** 2026-06-08

## Local configuration

| Variable | Status |
|----------|--------|
| `PITER_GUARDRAIL_ID` | **Unset** |
| `PITER_GUARDRAIL_VERSION` | **Unset** |

## AWS Bedrock Guardrail (account)

| Field | Value |
|-------|-------|
| ID | `rti921amc6u3` |
| Name | `incidentiq-demo-guardrail` |
| Status | **READY** |
| Version audited | **DRAFT** |
| Attached to Agent | **No** (`guardrailConfiguration: null`) |

## Policy summary (DRAFT)

### Topic policy (DENY)

| Topic | Input/Output action |
|-------|---------------------|
| `credential_exfiltration` | BLOCK — API keys, secrets, `.env` dumps |
| `unauthorized_production_changes` | BLOCK — destructive prod actions without approval |

### Content filters (partial list from API)

| Type | Strength |
|------|----------|
| VIOLENCE | MEDIUM (block in/out) |
| PROMPT_ATTACK | HIGH input block |

## App-level guardrails (always active)

Module: `app/guardrails.py`

- Blocks destructive SQL/Redis patterns (FLUSHALL, DROP, TRUNCATE, mass delete).
- Blocks policy bypass phrases ("disable guardrail", "send without token").
- Tested in `tests/test_guardrails.py`.

## Behavior when Bedrock Guardrail disabled/missing

| Layer | Behavior |
|-------|----------|
| Bedrock Guardrail | Not invoked — no account-level topic/content block from Bedrock |
| App guardrails | **Still active** via `validate_question()` before RAG call |
| Agent instruction | Safety rules embedded in system instruction |

## Tests

| Test file | Coverage |
|-----------|----------|
| `tests/test_guardrails.py` | Operator prompt blocking |
| `tests/test_validators.py` | Integration with question validation |
| No mocked Bedrock Guardrail allow/block | **Gap** — only app-level tests |

## Classification

| Item | Status |
|------|--------|
| Bedrock Guardrail resource | **Exists but not wired** |
| App guardrails | **Production-ready for demo** |
| Agent attachment | **Gap — planned enhancement** |

## Recommended setup (requires AWS mutation — do not run without approval)

1. Publish guardrail version from DRAFT → version `1`.
2. Attach to Bedrock Agent via `update-agent` + prepare.
3. Optionally set `PITER_GUARDRAIL_ID` / version in `.env` if direct KB path adds guardrail config later.

## Commands run (read-only)

```powershell
aws bedrock list-guardrails --max-results 10
aws bedrock get-guardrail --guardrail-identifier rti921amc6u3 --guardrail-version DRAFT
aws bedrock-agent get-agent --agent-id HH4YGSLZUE --query "agent.guardrailConfiguration"
```
