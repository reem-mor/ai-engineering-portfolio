# PITER Bedrock Live Validation

**Date:** 2026-06-08

## Mode A — `RAG_BACKEND=retrieve_and_generate` (default in Docker)

| Check | Result |
|-------|--------|
| Request succeeds | Yes |
| `mode=bedrock` in triage card | Yes |
| Grounded answer | Yes |
| Citations | Yes (≥1) |
| Tool enrichment | Yes — deploy, owner, impact, similar |
| Follow-up memory | Yes |
| Latency | Acceptable for demo (~10–20s class scenario) |

## Mode B — `RAG_BACKEND=agent`

| Check | Result |
|-------|--------|
| Agent ID | `HH4YGSLZUE` |
| Alias `live` | `O2EM03R4R3` → version 6 |
| KB associated | `RBTJM6NIG9` |
| Guardrail | `rti921amc6u3` v2 attached |
| Action groups | piter-* ENABLED; legacy incidentiq-ops DISABLED |
| `agent_smoke_test.py` | **7/7 PASS** |

## Error handling

- Invalid KB ID → local fallback (Phase B in `verify_live_demo.py`) — **PASS**
- IAM `ApplyGuardrail` fixed in prior AWS alignment commit

## Prior AWS reports

See `PITER_BEDROCK_AGENT_AWS_CHECK.md`, `PITER_INVOKE_AGENT_SMOKE_CHECK.md`, `evaluation/agent_smoke_results.md`
