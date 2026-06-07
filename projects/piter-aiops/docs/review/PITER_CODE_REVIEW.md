# PITER AiOps — Code Review

- **Author:** Re'em Mor
- **Date:** 2026-06-07
- **Scope:** backend routes/services, MCP layer, frontend API contracts, memory, datasets, use cases.
- **Method:** live exercise of every endpoint (mock mode) + static pattern scan + full test suite.

## Summary
One real defect found and **fixed** (HTTP 500 in escalation). Everything else is sound: all
endpoints return 200 or a graceful, structured 4xx/5xx; frontend↔backend contracts match; memory,
datasets, and the MCP layer work. Test suite **246 passed**.

## Bugs found & fixed
| Sev | Area | Finding | Fix |
| --- | ---- | ------- | --- |
| **High** | `POST /api/escalation/notify` | `jsonify(ok=False, **result)` raised `TypeError: got multiple values for keyword argument 'ok'` when the dispatch result already contained an `ok` key (unconfigured-recipient path) → **HTTP 500** instead of a clean gated 400. | `result.pop("ok", None)` before spreading; regression test added (`test_escalation_notify_unconfigured_recipient_returns_clean_error`). No notification is ever sent on this path. |
| **High (env)** | bootstrap / `check_sms_account_ready` | Raised `NoCredentialsError`/`BotoCoreError` with no AWS creds → crashed `/`, `/api/bootstrap`, `/console` offline. | Catch `BotoCoreError`, report SMS "not ready" (committed earlier in this pass). |

## Endpoints exercised (mock mode) — all healthy
| Endpoint | Result |
| -------- | ------ |
| `GET /health` | 200 `status=ok` |
| `GET /api/bootstrap` | 200 (execution-mode hint, notification settings) |
| `GET /api/demo-alert` | 200 `{ok, alert}` |
| `GET /api/alert-stream` | 200 `total=399, noise_suppressed=361, p1_count=1` |
| `GET /api/kb/manifest` | 200 |
| `POST /api/triage` | 200 grounded, 2 citations, all 4 tools, session id |
| `POST /api/follow-up` | 200 `memory_used=true, kind=owner` |
| `POST /ask` | 200 |
| `POST /api/workflow/triage` | 400 `empty_question` (correct validation) |
| `POST /api/escalation/notify` | 400 gated (no send) — was 500 before fix |
| `POST /documents/upload` | 400 `upload_disabled` in mock (graceful); type-rejection works when configured |

## Verified working
- **API calls:** every route returns structured JSON; no unhandled 500s after the fix.
- **MCP:** `mcp/server.py --selftest` OK; stdio JSON-RPC `initialize`/`tools/list`/`tools/call` work;
  `escalation_preview` masks recipient and never sends; 7 dedicated tests.
- **Frontend ↔ backend contracts:** `frontend/src/lib/api.ts` matches backend shapes
  (`notifyEscalation` sends `channel`; CSRF via `withCsrf`; `executionModeLabel` mirrors
  `_execution_mode_hint`).
- **Memory logic:** follow-up reuses session context (`memory_used=true`); new alert → new session;
  no cross-incident mixing (keyed by `session_id`).
- **Datasets:** 399 deterministic alerts, exactly 1 P1 trigger; test-backed
  (`test_source_data.py`, `test_data_corpus.py`).
- **Use cases:** Postgres-CPU demo scenario produces grounded card + 4 tool results + working
  follow-up in both Bedrock-fallback and local modes.

## Minor nits (non-blocking, not fixed)
| Area | Note | Why deferred |
| ---- | ---- | ------------ |
| `/documents/upload` | When S3 is unconfigured, the "upload disabled" check precedes type validation, so an unsupported file returns `upload_disabled` rather than `unsupported_type`. | Cosmetic ordering; both are safe refusals. In a configured env, type validation applies. |
| `/console` header | Shows `mode: —` until a triage runs (Jinja fallback). | Cosmetic; SPA dashboard shows execution mode prominently. |
| Logging | Correlation-id not on every path. | Tracked in `PITER_LOGS_TRACES_AUDIT.md` as an enhancement. |
| Bare `except Exception` | Present in `bedrock_agent_client`, `tool_router`, `bedrock_client`, `escalation_message`. | Intentional and documented (`noqa: BLE001` — tools/RAG must never crash the request; funneled through `translate()`). |

## Other `jsonify(**dict)` spread sites — checked, no collision
Lines 213/226/345/365/439/520 spread dicts that do **not** contain `ok`; verified by exercising the
endpoints (all 200). Only the escalation result carried its own `ok` (now handled).

## Verdict: **PASS** after the escalation fix. Backend, frontend, MCP, memory, and datasets are
solid and test-covered (246 passed).
