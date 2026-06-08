# PITER Memory & History Audit

## Implementation

| Component | File | Behavior |
|-----------|------|----------|
| Session store | `app/services/session_memory.py` | In-process dict, max sessions capped |
| Triage save | `triage_service.run_triage` → `save_triage` | Stores alert, citations, tool_outputs, triage_card |
| Follow-up | `run_follow_up` | Keyword router on owner/deploy/impact/similar; optional RAG |
| Agent memory | `bedrock_agent_client` session_id | Bedrock Agent session when `RAG_BACKEND=agent` |

## Teacher requirements

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Remembers last question | **PASS** | `append_followup`, follow-up tests |
| Previous conversations visible | **PARTIAL** | SPA/console show session thread; not persisted to disk |
| New incident → new session | **PASS** | `create_session` UUID |
| Memory does not mix incidents | **PASS** | Per session_id |
| Citations/tools saved | **PARTIAL** | Saved but follow-up prefers `tool_outputs` over `triage_card` |

## Wording (correct)

Use: *"The system stores, summarizes, retrieves, and reuses relevant investigation context within a session."*

Do not claim the model permanently learns.

## Gaps

1. Fix follow-up to read `triage_card` / `structured_analysis` first
2. Optional: SQLite/Redis session store for multi-worker production
3. UI: expose session history list (if not already in SPA sidebar)

## Tests

- `tests/test_agent.py` — follow-up memory postgres demo
- `verify_live_demo.py` — `memory_used=True` on follow-up (both phases)

Missing: P1 storm follow-up regression test.
