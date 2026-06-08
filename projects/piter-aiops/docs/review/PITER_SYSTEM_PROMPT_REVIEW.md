# PITER System Prompt Review

## Sources

| Location | Used when |
|----------|-----------|
| `app/bedrock_agent_client.py` — `AGENT_INSTRUCTION` | `invoke_agent`, `ensure_agent_alias.py` sync |
| `app/bedrock_client.py` — `RAG_GENERATION_PROMPT` | `retrieve_and_generate` |
| `app/guardrails.py` | Pre-flight on user questions |
| `app/local_agent.py` — `compose_answer` | Local fallback formatting |

## Required output sections (PITER)

| Section | Agent instruction | RAG prompt |
|---------|-------------------|------------|
| Priority | Yes | Yes |
| Investigation findings | Yes | Yes |
| Triage plan | Yes | Yes |
| Escalation recommendation | Yes | Yes |
| Resolution plan | Yes | Yes |
| Business impact | Yes | Yes |
| Sources | Yes | Yes |
| Confidence and uncertainty | Partial | Partial ("Confidence" in RAG template) |

## Instruction quality

**Strengths:**
- Explicit PITER workflow order
- Grounding rules ("never invent owners, deploys, contacts")
- Safety refusals (FLUSHALL, failover, WAF bypass, mass kill)
- Notification/allowlist bypass refusal

**Gaps:**
- Two prompts can drift — no single `prompts/` module
- Local `compose_answer` uses shorter Summary/Steps format (acceptable for fallback)
- Agent AWS copy may be stale until `ensure_agent_alias.py` run after edits

## Prompt injection

- `guardrails.py` blocks policy bypass phrases
- No Bedrock Guardrails content filter ID configured
- Upload docs could contain injection text — relies on KB chunking + model refusal

## Recommendation

1. Extract shared PITER section template to `app/prompts/piter_output.md` imported by both clients.
2. After local prompt edits, run `ensure_agent_alias.py` (AWS approval).
3. Add eval rubric in `evaluation/` for section presence (partially covered by smoke tests).
