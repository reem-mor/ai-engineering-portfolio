# PITER AiOps — Requirement Compliance Matrix

- **Author:** Re'em Mor
- **Date:** 2026-06-07

Statuses: **PASS** · **PARTIAL** · **FAIL** · **MOCKED** · **NOT VERIFIED** (cannot confirm in a
credential-less sandbox; verifiable only with a live `.env`).

| # | Requirement | Evidence in code/docs | Status | Gap | Fix |
| - | ----------- | --------------------- | ------ | --- | --- |
| 1 | Flask web app | `app/__init__.py` factory, `app/routes.py`, `app/spa.py`, `wsgi.py`; 238 tests pass | PASS | — | — |
| 2 | RAG over documents | 3-tier: `BedrockAgentClient` → `BedrockRagClient` (retrieve_and_generate) → `LocalRagClient` (TF-IDF), via `app/rag_factory.py` | PASS | Live path NOT VERIFIED here (no creds) | Demo with `.env` |
| 3 | MCP / tools | Bedrock action groups + `app/services/tool_router.py`; `docs/mcp.md`; no standalone server | PARTIAL | No runnable MCP server | Add read-only `mcp/` scaffold (Commit 5) |
| 4 | Docker | `Dockerfile` (node build + python runtime), `docker-compose.yml` (`piter-aiops:dev`, `8080`) | PASS | — | — |
| 5 | CSV/JSON/Pandas | `app/enrichment_tools.py` + `app/services/*` read `data/source/*.csv/.json`; pandas in `requirements.txt` | PASS | — | — |
| 6 | GitHub repo hygiene | `.gitignore` excludes `.env`; structured tree; but committed PII | PARTIAL | Personal PII committed | Redact (Commit 2) |
| 7 | README / run instructions | `README.md` (17 KB), `docs/live_demo.md`, `TESTING.md` | PASS | Minor refresh post-UI | Update in Workstream 8 |
| 8 | Working live demo | `/console` + SPA; `scripts/verify_live_demo.py` (29 checks) | PASS (offline) / NOT VERIFIED (live) | Live needs creds | Run with `.env` |
| 9 | KB connected to Agent | `scripts/setup_bedrock_agent.py` associates KB; `docs/bedrock_agent_setup.md` | NOT VERIFIED | Read-only sandbox | Verify via AWS console / read-only boto3 |
| 10 | boto3 `invoke_agent` | `app/bedrock_agent_client.py:120` `bedrock-agent-runtime.invoke_agent` | PASS (code) / NOT VERIFIED (live) | — | Demo with `.env` |
| 11 | Memory remembers last question | `app/services/session_memory.py`, `run_follow_up()`; verifier "follow-up used session memory" passes | PASS | In-memory only | Note Redis upgrade path |
| 12 | Previous conversation history | `session_memory` stores alert, citations, tool outputs, followups | PARTIAL | Single-process, non-persistent | Document; optional persistence |
| 13 | 4 Lambda functions | `action_groups/piter-recent-deployments`, `piter-service-context`, `piter-similar-incidents`, `piter-escalation` | PASS | Live names may be legacy `iiq-*` | Documented in `PITER_LAMBDA_ACTION_GROUP_AUDIT.md` |
| 14 | System prompt quality | `AGENT_INSTRUCTION` (`app/bedrock_agent_client.py:22`) + `RAG_GENERATION_PROMPT` (`app/bedrock_client.py:28`) | PASS | Two prompts (agent vs KB path) — both consistent | Documented in prompt review |
| 15 | Tests | 34 modules / **238 tests pass**; `pytest.ini` | PASS | — | Add notification edge tests if gaps |
| 16 | Security | `.env` ignored; guardrails regex; path-traversal protection; no `AKIA` | PARTIAL | Committed PII | Redact (Commit 2) |
| 17 | Guardrails | `app/guardrails.py` (destructive/bypass patterns) + agent safety rules; env `PITER_GUARDRAIL_*` documented | PARTIAL | Bedrock Guardrail resource NOT VERIFIED | Document enable path |
| 18 | S3 buckets | `app/upload_service.py`, `infra/bedrock_kb_s3_policy*.json`, prefix `projects/piter-aiops/data/sample_documents` | NOT VERIFIED | Read-only sandbox | Read-only AWS check |
| 19 | Logs / traces | `enableTrace=True` in `invoke_agent`; structured `logging` | PARTIAL | Correlation-id coverage uneven | `PITER_LOGS_TRACES_AUDIT.md` |
| 20 | Dataset quality | All 9 required files in `data/source/`; deterministic generators | PASS | Validate one-P1-trigger invariant | `PITER_DATASET_AUDIT.md` |
| 21 | KB quality | 16 MD docs w/ YAML front matter across 5 folders | PARTIAL | Author field; section completeness | Update (Commit 4) |
| 22 | UI/UX readiness | React/Vite SPA (dark SOC theme) + Jinja `/console` fallback | PARTIAL | Polish + label mock controls | UI commit (Commit 6) |
| 23 | Presentation / demo readiness | `docs/presentation_outline.md`, `docs/live_demo.md`, `docs/GRADING_CHECKLIST.md` | PASS | Refresh demo commands | Final report |

## Summary
- **PASS:** 11 · **PARTIAL:** 8 · **NOT VERIFIED (live AWS):** 4 (overlap on items gated by credentials)
- No outright **FAIL**. The credential-gated items are verifiable only in the graded environment.
