# PITER AiOps — Live AWS Smoke Summary (pre-class)

- **Run at:** 2026-06-04 (UTC)
- **Account:** `329597159579` (`admin-reem`)
- **Region:** `us-east-1`
- **KB:** `RBTJM6NIG9` · **Agent:** `HH4YGSLZUE` · **Alias:** `O2EM03R4R3` (live)
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`

## Results

| Suite | Script | Score | Verdict |
|-------|--------|-------|---------|
| Direct KB (RetrieveAndGenerate) | `scripts/kb_smoke_test.py` | **7/7** | RELIABLE — demo-safe |
| Ops questions (agent) | `scripts/agent_smoke_test.py --ops` | **3/3** | RELIABLE |
| Agent (invoke_agent) | `scripts/agent_smoke_test.py` | 5–6/7 | FLAKY — see below |

Detailed per-run tables: `smoke_results.md` (KB), `agent_ops_smoke_results.md` (ops),
`agent_smoke_results.md` (agent).

## Fix applied (real bug found)

The direct-KB path initially failed **0/7** with:

> ValidationException: `temperature` and `top_p` cannot both be specified for this model.

Claude Haiku 4.5 forbids sending both. Fixed in `app/bedrock_client.py` by pinning
`temperature=0.0` and removing `topP` from `textInferenceConfig`. Re-ran → **7/7 PASS**.

## Agent-path flakiness (honest risk)

The `invoke_agent` backend (`RAG_BACKEND=agent`) intermittently answers from the
model's own knowledge **without** querying the Knowledge Base, returning
`grounded=False` with **0 citations**. Measured on the exact demo scenario
("Postgres CPU is 95% on prod-db-1 postgres"): grounded in only **1 of 3** runs.

The app's local fallback fires only on a `BedrockError` exception, **not** on an
ungrounded zero-citation answer — so a flaky agent response would render a
citation-less card live. The 4-tool MCP enrichment, owner/escalation, business
impact, similar incidents and follow-up memory are produced by the app layer and
are identical regardless of RAG backend.

### Decision (demo-safe config)

`.env` set to `RAG_BACKEND=retrieve_and_generate` for the live AWS demo:
deterministic grounded citations (7/7) while keeping the full app-layer MCP
orchestration. The `invoke_agent` path remains available and teacher-aligned but
is flagged as unreliable for a live cited-RAG demo.

## Guaranteed fallback

`USE_BEDROCK=false` runs the fully offline local TF-IDF RAG + deterministic tools
demo (no AWS calls) — the never-fail rehearsal/backup path.

## Live `/console` end-to-end (`scripts/verify_live_demo.py`) — 29/29 PASS

Drives the exact class scenario (postgres / NJ-DGE / P2) through the Flask
client against the real `.env`.

- **Phase A — live AWS:** triage served by Bedrock (`mode=bedrock`), grounded
  with 3 citations (`runbook_db_cpu.md`), all 4 tools enriched
  (owner `dba-oncall`, impact `high`, 2 similar incidents, correlate ran),
  8 recommended steps, follow-up `memory_used=True`.
- **Phase B — simulated AWS-down (bad KB id → ResourceNotFoundException):** app
  transparently falls back to LOCAL (`mode=local`), still grounded with 2
  citations (`RB-007-postgres-cpu-high.md`), all 4 tools + follow-up memory
  intact. **The demo never fails.**
