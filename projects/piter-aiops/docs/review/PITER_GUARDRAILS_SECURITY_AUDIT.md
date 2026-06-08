# PITER Guardrails & Security Audit

## Application guardrails

| Control | File | Status |
|---------|------|--------|
| Destructive command block | `app/guardrails.py` | PASS |
| Policy bypass block | `app/guardrails.py` | PASS |
| Question validation | `app/validators.py` | PASS |
| Upload type/size | `app/upload_validators.py` | PASS |
| Operator prompts in agent/RAG | `bedrock_agent_client.py` | PASS |

## Bedrock Guardrails

| Item | Status |
|------|--------|
| `PITER_GUARDRAIL_ID` in config | **NOT FOUND** |
| Managed guardrail on retrieve_and_generate | **NOT VERIFIED** |

Recommendation: optional env vars + console guardrail for PII/topic deny — requires AWS approval.

## Secrets & repo hygiene

| Check | Status |
|-------|--------|
| `.env` gitignored | PASS |
| `.env.example` has placeholders only | PASS |
| PEM keys in repo | Spot-check: use `.gitignore` for `*.pem` |
| Hardcoded AWS account in docs/infra | Present as examples — OK for private course repo |
| Local `.env` has live tokens/recipients | **Risk if committed** — not staged |

## API security

| Item | Risk |
|------|------|
| CSRF exempt on blueprint | Medium for internet-exposed demo |
| CORS in development | `FRONTEND_DEV_ORIGIN` — OK for dev |
| `FLASK_SECRET_KEY` | Required; example uses placeholder |

## CSRF / auth

No end-user authentication — acceptable for course demo. Document network boundary.

## Dependency risk

Not scanned in this audit — run `pip audit` / Dependabot separately.

## Prompt injection

- KB documents could contain adversarial text
- Mitigation: grounding + app guardrails + operator training

## Tests

`tests/test_guardrails.py` — destructive and bypass patterns.
