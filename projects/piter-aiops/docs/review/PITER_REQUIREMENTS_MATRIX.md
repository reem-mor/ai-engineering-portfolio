# PITER Requirements Compliance Matrix

**Date:** 2026-06-08

| # | Requirement | Evidence | Status | Gap | Exact fix |
|---|-------------|----------|--------|-----|-----------|
| 1 | Flask web app | `app/__init__.py`, `app/routes.py`, gunicorn in Dockerfile | **PASS** | — | — |
| 2 | RAG over documents | `app/bedrock_client.py`, `app/services/local_rag.py`, `data/sample_documents/` | **PASS** | Local TF-IDF weaker on policy questions vs Bedrock | Document limitation |
| 3 | MCP / tools | `mcp/server.py`, `app/enrichment_tools.py`, Bedrock action groups | **PASS** | MCP is local contract layer, not production path | Already documented in `mcp/README.md` |
| 4 | Docker execution | `Dockerfile`, `docker-compose.yml` (`piter-aiops:dev`, :8080) | **PARTIAL** | Docker daemon not running on audit host | Re-run `docker compose up` before demo |
| 5 | Pandas / CSV / JSON | `app/services/data_access.py`, `data/source/*.csv`, `*.json` | **PASS** | — | — |
| 6 | Clean GitHub repo | `.gitignore` excludes `.env`; structured `projects/piter-aiops/` | **PARTIAL** | Uncommitted WIP; stale paths in some docs | Commit piter-aiops changes; scrub legacy paths |
| 7 | README + run instructions | `README.md`, `TESTING.md`, `docs/live_demo.md` | **PASS** | Some legacy `iiq`/`incident-rag` references | Phase 21 doc pass |
| 8 | Working live demo | `verify_live_demo.py` 29/29; `docs/LIVE_DEMO_CHECKLIST.md` | **PASS** | — | — |
| 9 | KB connected to Agent | AWS: KB `RBTJM6NIG9` ENABLED on agent `HH4YGSLZUE` | **PASS** | Agent display name still IncidentIQ | Rename agent in AWS (approval) |
| 10 | boto3 `invoke_agent` | `app/bedrock_agent_client.py`, `RAG_BACKEND=agent` path | **PASS** | Current `.env` uses `retrieve_and_generate` for demo stability | Document both paths; teacher demo can set `RAG_BACKEND=agent` |
| 11 | Memory remembers last question | `app/services/session_memory.py`, `run_follow_up` | **PASS** | Follow-up uses `tool_outputs` not full analysis card | Fix session payload (local) |
| 12 | Previous conversation history | `session_memory.append_followup`, UI history in SPA/console | **PASS** | In-memory only (not durable across restarts) | Document limitation |
| 13 | 4 Lambda functions | Local: `piter-*` folders + tests; AWS: 3× `iiq-*` + `incidentiq-ops` | **PARTIAL** | `piter-escalation` not deployed; 5th group `incidentiq-ops` on agent | Deploy escalation Lambda; disable or align ops group |
| 14 | System prompt quality | `AGENT_INSTRUCTION` in `bedrock_agent_client.py`, `RAG_GENERATION_PROMPT` in `bedrock_client.py` | **PASS** | Two prompts (agent vs RAG) — keep in sync | Single source file optional |
| 15 | Tests | 251 pytest; route, lambda, dataset, guardrail tests | **PASS** | Gaps on P1 follow-up, RB-012–014 analysis | Add tests |
| 16 | Security | Upload validation, guardrails.py, notification gates | **PARTIAL** | CSRF-exempt API; live notification mode in local `.env` | Demo network isolation; default mock mode in example |
| 17 | Guardrails | App regex guardrails | **PARTIAL** | No Bedrock Guardrails resource wired | Optional `PITER_GUARDRAIL_ID` |
| 18 | S3 buckets | `PITER_S3_BUCKET`, sync scripts | **PASS** | Legacy prefixes in IAM JSON templates | Update infra docs |
| 19 | Logs / traces | Structured logging in app/Lambdas | **PARTIAL** | No distributed trace IDs; CloudWatch not audited live | Phase 18 report |
| 20 | Dataset quality | 400 alert_stream, 1 trigger, validated in tests | **PASS** | `business_impact.json` only 3 entries vs 8 services | Expand impact matrix or document scope |
| 21 | Knowledge Base quality | 14 RB runbooks + sample_documents mirror | **PASS** | Some evaluation docs cite wrong S3 prefix | Fix paths |
| 22 | UI/UX readiness | React SPA committed under `app/static/spa/` | **PARTIAL** | `/console` Jinja still required for grading; some metrics mocked | See FINAL readiness |
| 23 | Presentation / demo | `docs/presentation_outline.md`, screenshots | **PARTIAL** | Screenshots reference old paths/console | Refresh capture scripts |
