# PITER AiOps — System Prompt Review

Read-only audit · 2026-06-06

## Prompt locations

| Location | Name / role | Used when |
|----------|-------------|-----------|
| `app/bedrock_agent_client.py` | `AGENT_INSTRUCTION` | Documented agent instruction (also reference for setup scripts) |
| `app/bedrock_client.py` | `RAG_GENERATION_PROMPT` | **Active** — injected into `retrieve_and_generate` |
| `app/local_agent.py` | `compose_answer()` template | Local/offline answers |
| `app/services/triage_service.py` | Orchestration (no LLM prompt) | Structures card, not generation |
| Lambda handlers | None (deterministic tools) | — |
| Frontend `App.tsx` | Code snippet showing `retrieve_and_generate` | UI education only |

## PITER workflow alignment

| Stage | Agent instruction | RAG prompt | Local compose |
|-------|-------------------|------------|---------------|
| Priority | **Yes** | **Yes** | Partial (via runbook) |
| Investigation | **Yes** | **Yes** | Summary line |
| Triage | **Yes** | **Yes** | Numbered steps |
| Escalation | **Yes** | **Yes** | Via runbook excerpt |
| Resolution | **Yes** | **Yes** | Steps |
| Business impact | **Yes** | **Yes** | Tool layer adds impact |
| Sources / citations | **Yes** | **Yes** | **Yes** |
| Confidence / uncertainty | **Yes** | **Yes** | Refusal when ungrounded |

## Strengths

- Explicit **do not invent** list (owners, deploys, on-call, policies).
- Structured output sections match recommended grading format.
- RAG prompt forbids tool-call syntax in output (`Action:`, JSON).
- Destructive-action guardrails in agent instruction.

## Gaps

| Gap | Severity |
|-----|----------|
| Agent instruction in code may diverge from Bedrock console agent instruction (verify in AWS console before agent demo) | P1 |
| No prompt injection hardening beyond "answer only from search results" | P2 |
| `MEMORY_ENABLED` not reflected in prompts | P3 |

## Proposed improved agent instruction (NOT applied — approval required)

```
You are PITER AiOps, an enterprise incident-response assistant for on-call engineers.

Workflow (mandatory sections in every answer):
Priority → Investigation findings → Triage plan → Escalation recommendation →
Resolution plan → Business impact → Sources → Confidence and uncertainty.

Rules:
- Use only knowledge-base retrieval and action-group tool results.
- Never invent owners, deployments, on-call names, or policies.
- If evidence is missing, say exactly what is missing and recommend escalation.
- Never recommend destructive production changes without explicit human approval.
- For P1–P3, always include escalation recommendation.

Current incident context may be provided in session attributes; reuse it for follow-ups
without repeating full triage unless asked.
```

## Teacher deliverable: "Explain the system prompt"

Use **`RAG_GENERATION_PROMPT`** for current live demo (`retrieve_and_generate`) and **`AGENT_INSTRUCTION`** for teacher-aligned agent path. Show both in slides with one sentence on why two paths exist.
