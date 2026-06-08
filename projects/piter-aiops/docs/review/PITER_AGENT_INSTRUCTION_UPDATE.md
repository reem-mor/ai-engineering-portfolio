# PITER Agent Instruction Update

**Date:** 2026-06-08  
**Agent:** `HH4YGSLZUE` (`incidentiq-triage-agent`)

## Source of truth

Live instruction synced from [`app/bedrock_agent_client.py`](../../app/bedrock_agent_client.py) → `AGENT_INSTRUCTION`.

## Required PITER format

The instruction enforces:

1. Priority → Investigation → Triage → Escalation → Resolution workflow
2. Grounding rules (KB + tools only; no invented owners/contacts/history)
3. Safety rules (refuse destructive ops, bypass attempts)
4. Output sections: Priority, Investigation findings, Triage plan, Escalation recommendation, Resolution plan, Business impact, Sources, Confidence and uncertainty

## Mutation

`setup_piter_aws_mutations.py` calls `update_agent` with `AGENT_INSTRUCTION` when guardrail attach runs. Instruction length on v4+: ~1628 characters.

## Validation

Agent smoke and P1 prompts return structured PITER-style answers with citations when grounded.

## Rollback

Restore prior instruction text from agent version 3 snapshot in AWS console or re-run `scripts/ensure_agent_alias.py` after reverting `AGENT_INSTRUCTION` in code.
