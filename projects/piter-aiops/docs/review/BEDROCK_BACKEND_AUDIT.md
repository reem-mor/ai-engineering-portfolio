# PITER AiOps — Bedrock Backend Audit

Read-only audit · 2026-06-06

## Routing verification (code)

| `RAG_BACKEND` | Client | boto3 service | API | Fallback |
|---------------|--------|---------------|-----|----------|
| `agent` | `BedrockAgentClient` | `bedrock-agent-runtime` | `invoke_agent` | Local on `BedrockError` in `routes._handle_ask` |
| `retrieve_and_generate` | `BedrockRagClient` | `bedrock-agent-runtime` | `retrieve_and_generate` | Local on `BedrockError` |
| `local` / `USE_BEDROCK=false` | `LocalRagClient` | — | TF-IDF over `data/sample_documents/` | N/A |

Factory: `app/rag_factory.py` — confirmed.

## Current active backend (local `.env`, non-secret flags)

| Setting | Value |
|---------|-------|
| `RAG_BACKEND` | **`retrieve_and_generate`** |
| `USE_BEDROCK` / `PITER_USE_BEDROCK` | **`true`** |
| `MOCK_MODE` | **`false`** |
| Agent ID configured | **Yes** |
| Agent alias configured | **Yes** |
| KB ID configured | **Yes** |

## Documentation vs runtime matrix

| Source | States primary backend | Matches `.env`? |
|--------|------------------------|-----------------|
| `.env.example` | `RAG_BACKEND=agent` | **No** |
| `README.md` (footer) | `invoke_agent` primary; `retrieve_and_generate` optional | **No** (env uses direct RAG) |
| `docs/architecture.md` | Agent primary; RetrieveAndGenerate fallback | **No** |
| `docs/LIVE_DEMO_CHECKLIST.md` | Intentional `retrieve_and_generate` for demo reliability | **Yes** |
| `evaluation/live_smoke_summary.md` | Demo-safe = direct KB (7/7); agent flaky (5–6/7) | **Yes** |
| `scripts/verify_live_demo.py` | Phase A uses `.env`; accepts `agent` or `retrieve_and_generate` | **Yes** |
| UI `/console` mode badge | `bedrock` or `local` only | **Partial** — does not distinguish agent vs direct RAG |

## UI truthfulness gap

`RagAnswer.mode` is `"bedrock"` for **both** `BedrockAgentClient` and `BedrockRagClient` (default in `bedrock_client.py` L102). The console pill therefore shows `bedrock` even when the teacher-required path is `invoke_agent` vs direct KB.

**Recommendation (P1):** Add explicit modes: `agent`, `retrieve_and_generate`, `local` — surface in API + console badge.

## Recommended policy (documented, not changed in this audit)

| Mode | Role |
|------|------|
| `agent` | Teacher-aligned primary — KB + action groups via Bedrock Agent |
| `retrieve_and_generate` | Demo-safe grounded citations when agent path is flaky |
| `local` | AWS-down / offline rehearsal (`USE_BEDROCK=false` or Bedrock exception fallback) |

## Live verification status

| Check | Status | Evidence |
|-------|--------|----------|
| Direct KB smoke | **7/7 reliable** | `evaluation/live_smoke_summary.md`, `scripts/kb_smoke_test.py` |
| Agent smoke | **5–6/7 flaky** (unguarded ungrounded answers) | `evaluation/live_smoke_summary.md` |
| E2E console demo | **29/29** | `scripts/verify_live_demo.py`, `evaluation/live_smoke_summary.md` |
| Unit tests (mocked RAG) | **190 pass** | `pytest` run 2026-06-06 |
| Live agent invoke (this session) | **Not run** | Avoided paid AWS calls per audit rules |

## Contradictions to resolve in docs (not code)

1. README/architecture say agent-primary; live demo deliberately uses direct RAG — add a **“Live demo config”** callout box.
2. `.env.example` should comment that course demo may set `retrieve_and_generate` while submission video should show `invoke_agent` if agent smoke passes.
