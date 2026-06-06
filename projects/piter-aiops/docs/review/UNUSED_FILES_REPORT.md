# PITER AiOps — Unused Files Report

Read-only audit · 2026-06-06 · **No files deleted.**

Evidence method: ripgrep imports, Flask blueprint registration, template `{% include %}`, Docker COPY lines, pytest collection, README/doc links, script references, and runtime path loads (`Path(__file__).parents`, `data_loader`, `local_rag`).

## Summary

| Verdict | Count |
|---------|------:|
| Safe delete candidates (after approval) | 4 |
| Keep — legacy name but referenced | 2 |
| Keep — historical docs (archive later) | 6 |
| Keep — generated but required | 2 |

## Candidate table

| Candidate | Evidence it is unused | Risk of deletion | Keep/Delete recommendation | Verification |
| --------- | --------------------- | ---------------- | -------------------------- | ------------ |
| `lambda-out.json` | No imports; single captured Lambda response; not referenced in tests/scripts except as stray artifact | Low | **Delete** after approval | `rg lambda-out` → docs only |
| `evaluation/pytest_output.txt` | Captured test log; not read by CI or scripts | Low | **Delete** after approval | `rg pytest_output.txt` → none |
| `.ec2_instance_id.txt` | Local EC2 launch helper output; gitignored pattern in `.gitignore` but file may exist locally | Low | **Delete** locally; add to `.gitignore` if tracked | Not in source imports |
| `.sg_id.txt` | Same as EC2 helper | Low | **Delete** locally; ensure gitignored | Not in source imports |
| `docs/PHASE0_AUDIT.md` | Superseded by this review; no runtime refs | Low | **Archive** to `docs/archive/` after approval | Historical only |
| `docs/UPGRADE_STATUS.md` | Point-in-time status; duplicated in `evaluation/live_smoke_summary.md` | Low | **Archive** after approval | No code refs |
| `docs/DEPLOY_STATUS.md` | Point-in-time deploy log | Low | **Archive** after approval | No code refs |
| `docs/cleanup_log.md` | Prior cleanup notes | Low | **Archive** after approval | No code refs |
| `PLAN.md` (repo root) | Planning scratchpad; not imported | Low | **Keep or archive** — useful context | Optional |
| `action_groups/incidentiq-ops/` | Legacy folder name | **Medium** | **Keep** | `setup_action_group.py` L35, `test_lambda_action_handler.py` L11 deploy primary ops AG |
| `infra/bedrock_kb_s3_policy.json` | Stale S3 prefix `incidentIQ-midproject` | **Medium** | **Keep until policy updated** — do not delete; fix path | Used as IAM template |
| `knowledge_base/runbooks/` vs `data/sample_documents/` | Two corpora; different naming (RB-00N vs friendly names) | **High** if deduped wrong | **Keep both** | Docker copies `knowledge_base/`; local RAG uses `data/sample_documents/`; see `CORPUS_RECONCILIATION.md` |
| `app/templates/_architecture.html`, `_deliverables.html`, etc. | Only used when `FORCE_LEGACY_UI=true` (SPA default) | Medium | **Keep** | Legacy UI fallback; referenced from `index.html` |
| `app/static/js/app.js` | Legacy UI JS | Medium | **Keep** | Referenced in legacy templates |
| `scripts/verify_console_demo.py` | Parallel to `verify_live_demo.py` | Low | **Keep** — different entry point | `rg verify_console_demo` |
| `scripts/kb_reconciliation_retrieval_check.py` | One-off eval helper | Low | **Keep** | Referenced in `CORPUS_RECONCILIATION.md` |
| `docs/review/_gen_inventory.py` | Inventory generator used once | Low | **Delete** after inventory frozen | This audit helper only |

## Files explicitly NOT unused (common false positives)

| Path | Why it stays |
| ---- | ------------ |
| `app/bedrock_agent_client.py` | `rag_factory` when `RAG_BACKEND=agent` |
| `app/bedrock_client.py` | `rag_factory` when `RAG_BACKEND=retrieve_and_generate` |
| `app/local_agent.py` | Offline + Bedrock error fallback |
| `app/enrichment_tools.py` | App-layer 4-tool orchestration (always runs on triage) |
| `scripts/agent_smoke_test.py`, `scripts/kb_smoke_test.py` | Live AWS verification (exist; referenced in README) |
| `app/static/spa/` | Committed production SPA; served when SPA enabled |
| `evaluation/test_questions.json` | `kb_smoke_test.py`, `test_data_corpus.py` |
| `lambda-out.json` | **Not** required — delete candidate |

## Missing-file false alarm (docs vs tree)

Earlier glob scans under-counted files. Verified present on disk:

- `scripts/agent_smoke_test.py`, `scripts/kb_smoke_test.py`, `scripts/build_corpus.py`
- `tests/test_agent.py`, `tests/test_agent_client.py`, `tests/test_flask_routes.py`
- Full `data/sample_documents/` corpus (24 files)
- `frontend/vite.config.ts` (if present — build succeeds via Docker)
