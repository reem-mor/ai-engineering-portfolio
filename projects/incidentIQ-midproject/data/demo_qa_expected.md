# Demo Q&A — Expected answer focus

Grounded answers should follow numbered steps from the corpus. These outlines are for graders and smoke tests.

## 1. Postgres CPU 95% on prod-db-1

**Question:** Postgres CPU is 95% on prod-db-1 — what is the runbook?

**Source:** `runbook_db_cpu.md`

**Expected steps:** Confirm alert → bastion → `pg_stat_activity` → cancel >5m queries → terminate if needed → check indexes → Patroni failover → escalate DBA if CPU >90% for 15m.

## 2. API 5xx on checkout

**Question:** API 5xx rate is above 2% on checkout — what should I check?

**Source:** `runbook_checkout_5xx.md`, `postmortem_2024_07.md`

**Expected steps:** Recent deploys → logs → DB CPU/slow queries → dependencies → rollback → escalate by severity.

## 3. Queue lag above 30 seconds

**Question:** Queue lag is above 30 seconds — what should I do?

**Source:** `runbook_queue_lag.md`

**Expected steps:** Worker health → queue depth → recent deploys → scale workers → inspect DLQ → escalate if lag increases.

## 4. Login failures after deployment

**Question:** Users cannot log in after deployment — what should I check?

**Source:** `runbook_auth_login.md`

**Expected steps:** Health endpoint → logs → release notes → JWT_SECRET/AUTH_DB_URL/TOKEN_ISSUER → DB connectivity → token expiry → rollback if widespread.

## 5. Tier-1 vs escalate

**Question:** How do I decide if an alert should be resolved at Tier 1 or escalated?

**Source:** `tier1_escalation_guide.md`, `escalation_policy.pdf`

**Expected:** Decision tree — resolve when runbook is safe/deterministic; escalate for high impact, data/security/payment risk, or when runbook requires specialist; document actions.
