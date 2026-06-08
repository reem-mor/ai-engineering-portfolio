# Corpus Reconciliation Report

**Generated:** 2026-06-06  
**Scope:** `knowledge_base/runbooks/RB-001` … `RB-010` vs `data/sample_documents/` (20 ingestible files) vs active S3 prefix `projects/piter-aiops/data/sample_documents/`  
**Bedrock KB:** `RBTJM6NIG9` · data source `YICXAB6WOG` · **single inclusion prefix** (no second prefix needed after reconciliation)

---

## Executive summary

| Category | Count |
|----------|------:|
| Exact duplicates | 0 |
| Partial overlaps (merge into existing Bedrock file) | 7 RB topics |
| Conflicting procedures (must not merge) | 1 (RB-009 vs `runbook_queue_lag.md`) |
| Unique RB runbooks (upload as new canonical files) | 3 |
| Sample docs with no RB counterpart (keep as-is) | 10 |
| **Target Bedrock corpus size** | **23 files** (20 preserved + 3 new) |

**Canonical source of truth:** `data/sample_documents/` only.  
**Do not** upload `knowledge_base/runbooks/` as a parallel S3 prefix.  
**Do not** keep two conflicting versions of the same procedure in the index.

After merge + upload, `knowledge_base/runbooks/` becomes a **deprecated mirror** (or removed) and local RAG reads the same canonical directory as Bedrock.

---

## Comparison matrix

| RB ID | RB file | Best sample match | Relationship | Conflicts | Recommended canonical file | Action |
|-------|---------|-------------------|--------------|-----------|--------------------------|--------|
| RB-001 | `RB-001-api-gateway-5xx-spike.md` | `api_gateway_5xx_runbook.txt` | Partial overlap | Gateway vs checkout scope split | `api_gateway_5xx_runbook.txt` (+ keep `runbook_checkout_5xx.md`) | **Enhance** gateway txt with RB-001 heading/metadata; skip RB upload |
| RB-002 | `RB-002-auth-login-failures.md` | `runbook_auth_login.md` | Partial overlap | Alert names differ (`AuthLoginErrorRate` vs `AuthLoginFailureRate`); `auth_service_runbook.md` is extended FAQ | `runbook_auth_login.md` | **Merge** RB-002 sections (SQL, dangerous actions, RB-008 cross-ref) into canonical file |
| RB-003 | `RB-003-settlement-backlog.md` | `runbook_settlement.md` | Partial overlap | Backlog/replay focus vs latency focus; complementary | `runbook_settlement.md` | **Merge** backlog + duplicate-settlement warnings from RB-003 |
| RB-004 | `RB-004-postgres-replica-lag.md` | `runbook_replication_lag.md` | Partial overlap (~high) | Same SQL/procedure; RB adds promote-replica warning | `runbook_replication_lag.md` | **Merge** RB-004 dangerous actions + RB id in heading |
| RB-005 | `RB-005-connection-pool-exhaustion.md` | `runbook_connection_pool.md` | Partial overlap (~near) | Nearly same steps; `database_connectivity_runbook.md` is broader connectivity | `runbook_connection_pool.md` | **Merge** RB-005 metadata; keep `database_connectivity_runbook.md` as related (no merge) |
| RB-006 | `RB-006-promotions-engine-latency.md` | *(none)* | **Unique** | N/A | `runbook_promotions_engine_latency.md` | **Create new** from RB-006; upload |
| RB-007 | `RB-007-postgres-cpu-high.md` | `runbook_db_cpu.md` | Partial overlap (~high) | Same core SQL; RB-007 richer (Patroni, detection checks) | `runbook_db_cpu.md` | **Merge** RB-007 content into existing file (smoke test expects this name) |
| RB-008 | `RB-008-redis-token-store-degradation.md` | *(none)* | **Unique** | N/A | `runbook_redis_token_store.md` | **Create new** from RB-008; upload |
| RB-009 | `RB-009-kafka-consumer-lag.md` | `runbook_queue_lag.md` | **Conflicting** | RB-009 = Kafka/settlement offsets; `runbook_queue_lag.md` = email-worker/DLQ | `runbook_kafka_consumer_lag.md` (new) + keep `runbook_queue_lag.md` | **Do not merge.** Create separate Kafka runbook; rename clarity in heading of queue file |
| RB-010 | `RB-010-deployment-rollback.md` | `deployment_rollback_sop.docx` | Partial overlap (binary) | DOCX is format-diverse SOP; RB-010 is richer markdown | `runbook_deployment_rollback.md` | **Create new** markdown canonical from RB-010; keep docx in corpus (no conflict) |

---

## Exact duplicates

None. No RB file is a byte-level or semantic duplicate of an existing sample document. Closest pairs (RB-005 / `runbook_connection_pool.md`, RB-007 / `runbook_db_cpu.md`) share procedures but differ in structure, metadata, and depth.

---

## Partial overlaps (merge, do not upload separate RB file)

### RB-001 → `api_gateway_5xx_runbook.txt`

- **Overlap:** Gateway 5xx triage, throttle/timeout, recovery validation.
- **RB-only value:** WAF/TLS checks, regulatory impact, `correlate_deployments` hook.
- **Canonical:** `api_gateway_5xx_runbook.txt` (preserves smoke-adjacent gateway retrieval).
- **Also keep:** `runbook_checkout_5xx.md` (downstream checkout path — not duplicate of RB-001).

### RB-002 → `runbook_auth_login.md`

- **Overlap:** Post-deploy login failure checklist, rollback, escalation.
- **RB-only value:** Audit SQL, signing-key warnings, explicit RB-008 dependency.
- **Conflict to resolve:** Unify alert name to `AuthLoginFailureRate` (matches smoke test file) and add `RB-002` in title line.
- **Keep separate:** `auth_service_runbook.md` as extended FAQ (reference doc, not procedure duplicate).

### RB-003 → `runbook_settlement.md`

- **Overlap:** settlement-svc, NJ-DGE, postgres dependency, escalation.
- **RB-only value:** Queue replay / idempotency warnings, backlog SQL.
- **Merge:** Add RB-003 identifier and "do not replay queue" block to settlement runbook.

### RB-004 → `runbook_replication_lag.md`

- **Overlap:** Replica lag SQL, primary CPU cross-ref, escalation.
- **RB-only value:** "Do not promote lagging replica", WAL archiving warning.
- **Merge:** Add RB-004 to heading; append dangerous-actions section.

### RB-005 → `runbook_connection_pool.md`

- **Overlap:** Hikari timeout symptom, idle-in-transaction SQL, escalation tiers.
- **RB-only value:** `correlate_deployments` leak check, regulatory PID documentation.
- **Merge:** Add RB-005 to heading; align step numbering with RB version.

### RB-007 → `runbook_db_cpu.md`

- **Overlap:** `pg_stat_activity` cancel/terminate SQL (identical core).
- **RB-only value:** Detection checks, Patroni failover step, richer escalation.
- **Merge:** Replace/enrich `runbook_db_cpu.md` body with RB-007 content; **retain filename** (required by `evaluation/test_questions.json` id 1).

### RB-010 → new `runbook_deployment_rollback.md`

- **Overlap:** Rollback decision procedure (DOCX covers same topic in binary form).
- **Not a conflict:** Markdown + DOCX can coexist; markdown becomes primary cited runbook.
- **Create:** `runbook_deployment_rollback.md` from RB-010 with RB id in heading.

---

## Conflicting procedures

### RB-009 vs `runbook_queue_lag.md`

| Aspect | RB-009 | `runbook_queue_lag.md` |
|--------|--------|------------------------|
| Technology | **Kafka** consumer groups | **Email-worker** / generic message queue |
| Alert | `KafkaConsumerLag` | `QueueLagHigh` |
| Risk | Offset reset on settlement stream | DLQ replay for notifications |
| Smoke test | Not directly tested | **Question #3** expects `runbook_queue_lag` |

**Resolution:** Do not merge. Create **`runbook_kafka_consumer_lag.md`** from RB-009. Add subtitle to `runbook_queue_lag.md`: *"Email / worker queue lag (not Kafka)"* to prevent future conflation.

---

## Unique runbooks (upload as new files only)

| New canonical file | Source | Topic |
|--------------------|--------|-------|
| `runbook_promotions_engine_latency.md` | RB-006 | Promotions engine p95 / cache miss |
| `runbook_redis_token_store.md` | RB-008 | Redis token store / auth cache degradation |
| `runbook_kafka_consumer_lag.md` | RB-009 | Kafka settlement consumer lag |

Plus one derived from RB-010:

| New canonical file | Source | Topic |
|--------------------|--------|-------|
| `runbook_deployment_rollback.md` | RB-010 | Controlled rollback / migration safety |

**Total new uploads: 4 files.**

---

## Sample documents with no RB counterpart (keep unchanged)

These remain in the Bedrock corpus as-is; no reconciliation needed.

| File | Role |
|------|------|
| `alerts_last_3mo.json` | Historical alert context |
| `monitoring_alerts_reference.md` | Alert dictionary |
| `tier1_escalation_guide.md` | Smoke test Q5 |
| `incident_history.csv` | Similar-incidents tool data + KB context |
| `postmortem_2024_07.md` | Historical postmortem |
| `postmortem_template.docx` | Template (binary) |
| `escalation_policy.pdf` | Policy (binary) |
| `on_call_handoff_checklist.pdf` | Checklist (binary) |
| `payment_service_latency_runbook.txt` | PSP failover (distinct from RB-006 promotions) |
| `auth_service_runbook.md` | Extended auth FAQ (supplement to `runbook_auth_login.md`) |
| `database_connectivity_runbook.md` | Broad connectivity (supplement to pool/replica runbooks) |

---

## Recommended canonical filename convention

```
# RB-00N: Human title
**Runbook ID:** RB-00N
...
```

- **Stable descriptive filename** for S3/Bedrock (e.g. `runbook_db_cpu.md`).
- **RB identifier** in H1 or metadata line for grading cross-reference.
- **Do not** use `RB-00N-*.md` as S3 object names (avoids duplicate index entries alongside merged files).

---

## Planned file ledger (execution)

| File | Disposition |
|------|-------------|
| `runbook_db_cpu.md` | **Changed** — merge RB-007 |
| `runbook_auth_login.md` | **Changed** — merge RB-002 |
| `runbook_settlement.md` | **Changed** — merge RB-003 |
| `runbook_replication_lag.md` | **Changed** — merge RB-004 |
| `runbook_connection_pool.md` | **Changed** — merge RB-005 |
| `api_gateway_5xx_runbook.txt` | **Changed** — add RB-001 metadata + gateway-only steps |
| `runbook_queue_lag.md` | **Changed** — clarify not Kafka |
| `runbook_promotions_engine_latency.md` | **Uploaded (new)** |
| `runbook_redis_token_store.md` | **Uploaded (new)** |
| `runbook_kafka_consumer_lag.md` | **Uploaded (new)** |
| `runbook_deployment_rollback.md` | **Uploaded (new)** |
| `RB-001` … `RB-010` in `knowledge_base/runbooks/` | **Reconciled** — content absorbed; directory deprecated or symlinked |
| All other 13 sample_documents | **Skipped** (unchanged) |
| `knowledge_base/runbooks/` as S3 prefix | **Skipped** — not created |
| Legacy `incident-rag-bedrock/` S3 prefix | **Skipped** — not wired to KB |

---

## AWS sync requirements (unchanged infrastructure)

- **No** new bucket, KB, or vector store.
- **Single** data source prefix: `projects/piter-aiops/data/sample_documents/`
- IAM policy already allows this prefix (v3); no second prefix required.
- After S3 sync: `start-ingestion-job` → **0 failed**, ~23 scanned.
- Retest: `py -3.12 scripts/kb_smoke_test.py` (7/7) + retrieval spot checks for RB-tagged topics and new unique scenarios (promotions, redis, kafka).

---

## Local RAG alignment

Update [`app/services/local_rag.py`](app/services/local_rag.py):

- **Primary:** `data/sample_documents/` (markdown/text only for chunking).
- **Remove** `_PRIMARY_DIR = knowledge_base/runbooks` precedence.
- Update tests referencing `RB-007-postgres-cpu-high.md` document name → `runbook_db_cpu.md` with RB-007 in content.

---

## Execution log (2026-06-06)

**Canonical source:** `data/sample_documents/` only (no second S3 prefix, no new bucket/KB/vector store).

**Ingestion job:** `G4U131YDRV` — COMPLETE  
- Scanned: **24** · New indexed: **4** · Modified: **8** · Failed: **0**

**Verification:**
- `py -3.12 scripts/kb_smoke_test.py` → **7/7 PASS**
- `py -3.12 scripts/kb_reconciliation_retrieval_check.py` → **5/5 PASS** (RB-001, RB-006, RB-008, RB-009, RB-010)

### File ledger

| File | Action |
|------|--------|
| `runbook_db_cpu.md` | **Changed** — merged RB-007 |
| `runbook_auth_login.md` | **Changed** — merged RB-002 |
| `runbook_settlement.md` | **Changed** — merged RB-003 |
| `runbook_replication_lag.md` | **Changed** — merged RB-004 |
| `runbook_connection_pool.md` | **Changed** — merged RB-005 |
| `api_gateway_5xx_runbook.txt` | **Changed** — merged RB-001 metadata/steps |
| `runbook_queue_lag.md` | **Changed** — clarified email queue (not Kafka) |
| `incident_history.csv` | **Uploaded** — re-synced (unchanged content, included in job) |
| `runbook_promotions_engine_latency.md` | **Uploaded (new)** — RB-006 |
| `runbook_redis_token_store.md` | **Uploaded (new)** — RB-008 |
| `runbook_kafka_consumer_lag.md` | **Uploaded (new)** — RB-009 |
| `runbook_deployment_rollback.md` | **Uploaded (new)** — RB-010 |
| `knowledge_base/runbooks/RB-001` … `RB-010` | **Reconciled** — not uploaded; see `knowledge_base/runbooks/README.md` |
| Remaining 12 sample_documents (pdf/docx/json/etc.) | **Skipped** — unchanged, preserved in index |
| `knowledge_base/runbooks/` S3 prefix | **Skipped** — not created |
| Legacy `incident-rag-bedrock/` S3 prefix | **Skipped** — not wired to data source |

**Code/docs updated:** `app/services/local_rag.py`, `app/local_agent.py`, tests, `docs/bedrock_kb_setup.md`, `docs/architecture.md`, `docs/UPGRADE_STATUS.md`, `docs/cleanup_log.md`, `data/sample_documents/README.md`

---

## Stale documentation — status (2026-06-08)

| File | Status |
|------|--------|
| `docs/bedrock_kb_setup.md` | Uses `piter-aiops` prefix |
| `data/sample_documents/README.md` | S3 path + RB id convention |
| `docs/cleanup_log.md`, `code_review.md`, `teacher_submission_email.md` | Updated — legacy names noted where historical |
| `docs/architecture.md`, `UPGRADE_STATUS.md` | One corpus, `piter-aiops` prefix |
| `scripts/build_corpus.py` header | Output path → `projects/piter-aiops/` |
| `evaluation/qa_showcase.md`, `screenshots/README.md` | Canonical S3 prefix |
