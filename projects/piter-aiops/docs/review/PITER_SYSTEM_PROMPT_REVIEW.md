# PITER AiOps — System Prompt Review

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Prompt sources (two, by path — both consistent)
1. **Agent instruction** — `AGENT_INSTRUCTION` in `app/bedrock_agent_client.py:22`
   (also used by `scripts/setup_bedrock_agent.py` to provision the Bedrock Agent).
2. **KB-path generation prompt** — `RAG_GENERATION_PROMPT` in `app/bedrock_client.py:28`
   (used by `retrieve_and_generate`).

These are the single authoritative sources; the local fallback composes a structurally similar answer.

## Review against requirements
| Criterion | Agent instruction | KB prompt | Verdict |
| --------- | ----------------- | --------- | ------- |
| Role clarity | "enterprise SRE assistant…" | "enterprise incident-response assistant" | PASS |
| Five PITER stages enforced | Mandatory ordered workflow 1–5 | Same structure | PASS |
| Tool-use instructions | "use tool results only" | n/a (KB path) | PASS |
| KB-use instructions | "use KB citations only" | "Answer ONLY using the search results" | PASS |
| Memory-use | session attributes feed follow-ups | n/a | PASS |
| Anti-hallucination | "never invent owners/versions/contacts/incidents" | "cite from search results" | PASS |
| Missing-evidence behavior | 'state "Not in knowledge base"' | "state missing data" | PASS |
| Source/citation rules | every step cites runbook/policy/incident | "Sources:" section required | PASS |
| Escalation safety | name on-call from policy only | escalate only if evidence supports | PASS |
| Destructive-action confirmation | explicit REFUSE list (FLUSHALL, DROP, failover, WAF/MFA, scale-to-zero…) + human sign-off | n/a | PASS |
| Concise operational format | fixed 8-section output | same 8 sections | PASS |
| Prompt-injection resistance | "never bypass allowlists/tokens/audit"; "do NOT emit tool calls/JSON" | "Do NOT emit tool calls, JSON, or 'Action:' lines" | PASS |

## Findings
- Both prompts already match the task's desired PITER instruction almost verbatim and add a strong
  non-negotiable safety section. **No changes required.**
- Minor note: two prompts exist by necessity (agent vs direct-KB path). They are consistent; keep
  both in sync. Documented here as the canonical pair.

## Verdict: **PASS** — enterprise-grade, anti-hallucination, injection-resistant.
