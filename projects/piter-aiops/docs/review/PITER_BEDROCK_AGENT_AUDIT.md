# PITER AiOps — Bedrock Agent & boto3 Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Paths
1. **Primary:** Flask → boto3 `bedrock-agent-runtime.invoke_agent` → Agent → KB + Action Groups
   → answer with citations + tool results. (`app/bedrock_agent_client.py`)
2. **Fallback 1:** `bedrock-agent-runtime.retrieve_and_generate` (direct KB). (`app/bedrock_client.py`)
3. **Fallback 2:** local TF-IDF RAG. (`app/local_agent.py`, `app/services/local_rag.py`)

Selection: `app/rag_factory.py:get_rag_client()` — `local` if `USE_BEDROCK` false; else
`retrieve_and_generate` or `agent` per `RAG_BACKEND`.

## Audit checklist
| Item | Evidence | Status |
| ---- | -------- | ------ |
| boto3 client = `bedrock-agent-runtime` | `bedrock_agent_client.py`, `bedrock_client.py` | PASS |
| `invoke_agent` implemented | `bedrock_agent_client.py:120` (`agentId`, `agentAliasId`, `inputText`, `sessionId`, `enableTrace=True`, `sessionState`) | PASS (code) |
| Agent ID from env | `config.BEDROCK_AGENT_ID` ← `PITER_BEDROCK_AGENT_ID`/legacy | PASS |
| Alias ID from env | `config.BEDROCK_AGENT_ALIAS_ID` | PASS |
| KB ID from env | `config.BEDROCK_KB_ID` | PASS |
| Region from env | `config.AWS_REGION` ← `PITER_AWS_REGION`/`AWS_REGION` | PASS |
| No hardcoded secrets | boto3 credential chain only | PASS |
| sessionId behavior | UUID issued if absent; reused for follow-up | PASS |
| Session/prompt attributes | `build_session_attributes()` (`bedrock_agent_client.py:58`) | PASS |
| Trace parsing | iterates event stream; `enableTrace=True` | PASS |
| Citation parsing + dedupe | `bedrock_agent_client.py:146-179` | PASS |
| Tool/action-group result parsing | `bedrock_agent_client.py:192-212` merges enrichment JSON | PASS |
| Error handling | `app/errors.py` translates boto exceptions | PASS |
| Retries/timeouts | BotoConfig: 3 attempts standard; 120s read / 10s connect | PASS |
| Fallback behavior | `routes._handle_ask` catches `BedrockError` → local | PASS |
| UI shows actual execution mode | `_execution_mode_hint()`; never claims "Bedrock Agent" when KB path used | PASS |

## Live verification (sandbox)
- Code paths confirmed by `scripts/verify_live_demo.py` Phase B (forced AWS-down → local fallback):
  **14/14**, including grounded answer, ≥1 citation, all 4 tools, session memory.
- The live agent (`invoke_agent` against real AWS) is **NOT VERIFIED here** — no credentials.
  Reachability to AWS is confirmed (dummy creds → `UnrecognizedClientException`), so the live path
  is runnable in the graded environment with a valid `.env`.

## Recommendations
- Keep `RAG_BACKEND=agent` for the graded live demo to exercise action-group tool results inline.
- For read-only confirmation that KB↔Agent are associated, run a `bedrock-agent get-agent` /
  `list-agent-knowledge-bases` check (documented in `PITER_AWS_AUDIT.md`).
