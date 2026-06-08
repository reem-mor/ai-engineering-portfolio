# PITER Guardrail Attachment

**Date:** 2026-06-08  
**Guardrail:** `rti921amc6u3` (`incidentiq-demo-guardrail`)  
**Published version:** **2** (READY)

## Attachment

| Scope | Guardrail v2 |
|-------|----------------|
| Agent DRAFT | Attached |
| Agent version 4+ | Attached |
| Live alias v6 | **Active** |

## IAM fix (required)

After attachment, `invoke_agent` returned `accessDeniedException` until the agent role gained:

```json
{
  "Sid": "BedrockApplyGuardrail",
  "Action": ["bedrock:GetGuardrail", "bedrock:ApplyGuardrail"],
  "Resource": "arn:aws:bedrock:us-east-1:329597159579:guardrail/rti921amc6u3"
}
```

Applied via `scripts/setup_piter_aws_mutations.py` → `incidentiq-agent-resource`.

## Validation

| Test | Result |
|------|--------|
| Safe runbook question | **PASS** — grounded citations |
| Off-topic (Tokyo restaurant) | **PASS** — no citations, refusal-style answer |
| P1 incident triage | **PASS** |
| App operator guardrails (`app/guardrails.py`) | Unchanged; pytest pass |

## Rollback

1. `update_agent` without `guardrailConfiguration`
2. Prepare + new alias version
3. Remove `BedrockApplyGuardrail` statement only if guardrail detached
