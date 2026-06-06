# PITER AiOps — Knowledge Base Audit

Read-only audit · 2026-06-06

## Corpus locations

| Location | Files | Used by |
|----------|------:|---------|
| `data/sample_documents/` | 24 | Local RAG, S3 sync, Bedrock KB source, Lambda CSV/JSON data |
| `knowledge_base/runbooks/` | 10 RB-00N markdown | Docker image COPY (offline packaged runbooks) |
| S3 `projects/piter-aiops/data/sample_documents/` | Synced from local | Bedrock KB `RBTJM6NIG9` (per eval docs) |

**Note:** Dual corpus is intentional but naming differs (`runbook_db_cpu.md` vs `RB-007-postgres-cpu-high.md`). Reconciliation documented in `evaluation/CORPUS_RECONCILIATION.md`.

## Category coverage

| Category | Files | Quality | Missing data | Duplicates | Recommended fix |
| -------- | ----: | ------- | ------------ | ---------- | --------------- |
| Runbooks | 11+ MD/TXT in sample_docs + 10 RB in knowledge_base | **Strong** — concrete steps, RB IDs | None critical for demo scenario | Parallel RB-007 vs `runbook_db_cpu.md` | Document mapping table in README; keep both until S3/KB unified |
| Deployment notes | `runbook_deployment_rollback.md`, RB-010, DOCX SOP | Good | — | Overlap with rollback runbook | Acceptable |
| Service ownership | Via `action_groups/*/data/service_catalog.json` (not KB prose) | Tool data, not KB | Owner prose not in all runbooks | — | OK — tools supply owners |
| Escalation policies | `tier1_escalation_guide.md`, `escalation_policy.pdf` | Good | — | — | Keep |
| Priority definitions | Escalation PDF + tier1 guide | Adequate | P3/P4 examples sparse | — | Optional: add P3 example |
| Past incidents | `incident_history.csv`, `alerts_last_3mo.json`, postmortems | **Strong** (30-row CSV) | — | Some overlap postmortem vs history | Keep |
| Known errors | Monitoring reference MD | Good | — | — | Keep |
| Architecture | `monitoring_alerts_reference.md`, README architecture | Adequate | No standalone architecture.md in corpus | — | Optional KB doc |
| Troubleshooting | Per-service runbooks | **Strong** | — | — | Keep |
| Monitoring alerts | `monitoring_alerts_reference.md` | Good | — | — | Keep |
| Business-impact rules | `impact_matrix.csv` in Lambda data dirs | Tool-layer, not KB | Not in markdown corpus | — | OK for demo |

## Demo question coverage (evaluation set)

`evaluation/test_questions.json` — 7 cases: 5 grounded, 1 refusal, 1 validation error.

| Question theme | Covered? |
|----------------|----------|
| What changed recently? | Via correlate tool + deploy CSV (app layer) |
| Which service affected? | Alert form + runbooks |
| Who owns service? | `lookup_owner_and_escalation` tool |
| Priority assignment? | PITER prompt + severity in alert |
| Escalation path? | tier1 guide + tool |
| On-call? | service_catalog.json |
| Similar incidents? | `find_similar_incidents` + history CSV |
| Applicable runbook? | **Yes** — RB-007 / runbook_db_cpu for demo |
| First checks? | Runbook numbered steps |
| Business impact? | `score_business_impact` tool |
| Source citations? | Bedrock KB or local TF-IDF |

## Stale / inconsistent items

| Issue | Severity |
|-------|----------|
| `infra/bedrock_kb_s3_policy.json` still references `incidentIQ-midproject` prefix | P1 doc/infra |
| `data/sample_documents/README` references `scripts/build_corpus.py` — **exists** | OK |
| Binary corpus files (PDF/DOCX) present locally | OK for KB diversity requirement |

## Secrets / PII scan (sample)

- Corpus README claims synthetic fictional data — spot-check aligns (fictional incident IDs, no AKIA patterns in repo grep).
- **Do not** commit `.env` (gitignored ✓).
