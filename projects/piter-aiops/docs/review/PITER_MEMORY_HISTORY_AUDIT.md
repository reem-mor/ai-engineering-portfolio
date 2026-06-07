# PITER AiOps — Memory & History Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Implementation
`app/services/session_memory.py` — thread-safe, process-local store (max 200 sessions, LRU evict).
Session record: `session_id`, `created_at`, `alert`, `citations`, `tool_outputs`, `triage_card`,
`followups[]`. Multi-turn via `create_session` → `save_triage` → `append_followup`;
follow-ups handled by `services/triage_service.run_follow_up()`.

## Checklist
| Item | Evidence | Status |
| ---- | -------- | ------ |
| Remembers last question | follow-up reuses session context | PASS |
| Follow-up uses prior incident context | `run_follow_up` classifies (owner/deploy/impact/summary) from stored card | PASS |
| Previous conversations saved | `followups[]` per session | PASS |
| History viewable | exposed via session payload / triage card | PARTIAL (API yes; dedicated UI history list is light) |
| Recent incidents reopen/summarize | summary follow-up kind | PARTIAL |
| No cross-incident mixing | keyed by `session_id` | PASS |
| Stable session IDs | UUID issued, reused | PASS |
| New incident → new session | `create_session(alert)` | PASS |
| Citations + tool calls saved | stored in session | PASS |
| Execution mode saved | mode on card | PASS |
| Status saved | triage card status | PASS |
| Reset option | `session_memory.reset()` (tests) | PARTIAL (no user-facing reset button) |

## Correct wording
"The system **stores, summarizes, retrieves, and reuses** relevant investigation context."
It does **not** permanently train/learn the model.

## Gaps / recommendations (non-blocking)
- Memory is in-process and ephemeral (lost on restart / not shared across workers). Documented as a
  demo constraint with a Redis/Dynamo upgrade path.
- Optional: surface a "Context Memory" history list + reset control in the SPA (UI commit).

## Verified
`scripts/verify_live_demo.py`: "follow-up used session memory" passes in both phases.
