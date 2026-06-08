# PITER AWS Readiness Report — Final

**Audit date:** 2026-06-08  
**Project:** PITER AiOps (Priority → Investigation → Triage → Escalation → Resolution)  
**Account:** `329***579` · **Region:** `us-east-1` · **Profile:** `reemmor`  
**Constraint:** Read-only AWS audit — **no mutations performed**

## Executive summary

PITER AiOps is **demo-ready today** using the **`retrieve_and_generate`** path configured in `.env`. The **`invoke_agent`** path is also **verified working** but is not the current default RAG backend. Production-alignment gaps (legacy naming, missing `piter-escalation` on AWS, guardrail not attached to agent, SMS sandbox) are **non-blocking for the class demo** if you stay on the direct KB path and use notification confirmation gates.

### Decision: **B — Ready for demo with direct KB path; Agent production alignment remains next step**

---

## Readiness scorecard

| # | Area | Score (0–5) | Status |
|---|------|-------------|--------|
| 1 | Overall AWS readiness | **4.0 / 5** | Demo-ready with noted gaps |
| 2 | Bedrock Agent | 4 | PREPARED, strong PITER instruction |
| 3 | Bedrock Agent alias | 5 | PREPARED, routes to v3 |
| 4 | Knowledge Base association | 5 | ENABLED on agent v3 |
| 5 | boto3 invoke_agent | 4 | **PASS** (27s, grounded, tools) |
| 6 | retrieve_and_generate fallback | 5 | **Default path; 29/29 demo checks** |
| 7 | Local fallback | 5 | **PASS** when KB unavailable |
| 8 | Action groups | 3 | Legacy `iiq-*` + `incidentiq-ops`; functional |
| 9 | Four Lambda functions | 3 | **3/4 deployed** (escalation local only) |
| 10 | S3 bucket | 5 | Encrypted, blocked public, 28 docs |
| 11 | Guardrails | 3 | App-level strong; Bedrock guardrail not attached |
| 12 | SNS/SES | 3 | Configured; **SMS sandbox** |
| 13 | EC2 | N/A | None running (Docker demo) |
| 14 | CloudWatch logs | 4 | No Lambda errors in 7d |
| 15 | IAM/security | 4 | Functional; admin user — tighten for prod |
| 16 | Memory/session | 4 | Session ID + follow-up memory verified |
| 17 | System prompt quality | 5 | Full PITER workflow + grounding rules |
| 18 | Demo readiness | 4 | **Ready** on current config |

---

## Detailed findings

### Bedrock Agent (`HH4YGSLZUE` / alias `O2EM03R4R3`)

- Status: **PREPARED**, alias **ACCEPT_INVOCATIONS**, version **3**.
- Model: Claude Haiku 4.5 inference profile.
- Instruction matches PITER format and anti-hallucination rules (see Phase 4 report).
- KB `RBTJM6NIG9` **ENABLED**.

### invoke_agent vs retrieve_and_generate

| Path | `.env` today | Verified |
|------|--------------|----------|
| `retrieve_and_generate` | **Yes (default)** | 29/29 live demo |
| `agent` (`invoke_agent`) | No (override only) | P1 bet-service smoke **PASS** |

**Recommendation for submission video:** Run one scene with `RAG_BACKEND=agent` to show teacher-aligned orchestration; keep demo on `retrieve_and_generate` for citation reliability.

### Action groups and Lambdas

**Deployed:** `iiq-correlate`, `iiq-context`, `iiq-similar`, `incidentiq-actions`  
**Not deployed:** `piter-escalation`  
**Legacy on agent:** `incidentiq-ops` (ENABLED) — classify for later disable  
**Stale:** `incidentiq-ops-test` (DISABLED)

### Knowledge Base

- **ACTIVE**, retrieval returns relevant runbooks for all four audit queries.
- Watch ingestion job `340P2YZ4YF` (20 failed docs) — non-blocking today.

### Guardrails

- Account guardrail `rti921amc6u3` exists (READY) but **not attached** to agent.
- `app/guardrails.py` active; tests pass.

### Notifications

- SNS topic + SES sender verified.
- **SMS sandbox = true** — verify demo phone before live SMS.
- Confirmation token + allowlist + max-sends gates active.

### Infrastructure

- **No EC2** — Docker on `:8080` is healthy.
- S3 corpus secure and aligned with PITER prefix.

---

## Gaps requiring AWS write approval

| Priority | Gap | AWS mutation required |
|----------|-----|------------------------|
| P2 | Deploy `piter-escalation` Lambda + action group | Lambda create/update, agent prepare |
| P2 | Attach Bedrock Guardrail to agent | `update-agent`, prepare |
| P3 | Rename `iiq-*` → `piter-*` action groups/Lambdas | Lambda + agent version bump |
| P3 | Disable/remove `incidentiq-ops` on agent | Agent update |
| P3 | Delete `incidentiq-ops-test` disabled group | Agent/console cleanup |
| P3 | Exit SNS SMS sandbox / SES production | Support request |
| P4 | Rename KB/agent console display names | Metadata update |
| P4 | Re-run KB sync after local runbook additions | S3 upload + ingestion job |

---

## Recommended AWS changes (exact sequence — approval required)

### 1. Deploy piter-escalation (highest value)

1. `aws lambda create-function` (or update) from `action_groups/piter-escalation/`
2. Attach action group with `openapi_schema.yaml` → agent draft version
3. `prepare-agent` → update alias `live`
4. Test with confirmation token (no send until approved)

**Rollback:** Disable action group; revert alias to previous agent version (v3).

### 2. Attach guardrail

1. Publish guardrail DRAFT → version 1
2. `update-agent` with `guardrailConfiguration`
3. Prepare agent

**Rollback:** Remove guardrailConfiguration; re-prepare.

### 3. Legacy cleanup (post-demo)

1. Disable `incidentiq-ops` action group
2. Delete `incidentiq-ops-test`
3. Optional: create `piter-*` Lambdas mirroring `iiq-*` and swap action group executors

**Rollback:** Re-enable previous action groups on new agent version.

---

## Cost / risk notes

- **Bedrock:** Haiku 4.5 + KB retrieval — low per-query cost; agent path ~27s latency may increase token use.
- **Lambda:** 4 functions × 256MB × 15s max — negligible at demo volume.
- **S3 Vectors KB:** Storage + query charges — monitor if re-indexing large corpora.
- **SNS SMS sandbox:** No cost if not sending; live SMS incurs per-message fees.
- **IAM:** Broad admin user — acceptable for lab; not for production.

---

## Demo readiness checklist

- [x] KB ACTIVE, retrieval relevant
- [x] `retrieve_and_generate` live path 29/29
- [x] `invoke_agent` smoke PASS
- [x] Local fallback PASS
- [x] Docker health OK
- [x] pytest 271/271
- [x] Citations + enrichment tools in live demo
- [x] Session memory on follow-up
- [ ] SMS live send (sandbox constraint — verify recipient first)
- [ ] Agent path as default (optional for submission narrative)

---

## Report index

| Phase | Document |
|-------|----------|
| 1 | [PITER_AWS_PHASE_ENV_CHECK.md](./PITER_AWS_PHASE_ENV_CHECK.md) |
| 2 | [PITER_AWS_IDENTITY_CHECK.md](./PITER_AWS_IDENTITY_CHECK.md) |
| 3 | [PITER_KNOWLEDGE_BASE_AWS_CHECK.md](./PITER_KNOWLEDGE_BASE_AWS_CHECK.md) |
| 4 | [PITER_BEDROCK_AGENT_AWS_CHECK.md](./PITER_BEDROCK_AGENT_AWS_CHECK.md) |
| 5 | [PITER_INVOKE_AGENT_SMOKE_CHECK.md](./PITER_INVOKE_AGENT_SMOKE_CHECK.md) |
| 6 | [PITER_LAMBDA_ACTION_GROUP_AWS_CHECK.md](./PITER_LAMBDA_ACTION_GROUP_AWS_CHECK.md) |
| 7 | [PITER_S3_AWS_CHECK.md](./PITER_S3_AWS_CHECK.md) |
| 8 | [PITER_GUARDRAILS_AWS_CHECK.md](./PITER_GUARDRAILS_AWS_CHECK.md) |
| 9 | [PITER_SNS_SES_AWS_CHECK.md](./PITER_SNS_SES_AWS_CHECK.md) |
| 10 | [PITER_EC2_DOCKER_CHECK.md](./PITER_EC2_DOCKER_CHECK.md) |
| 11 | [PITER_LOGS_TRACES_AWS_CHECK.md](./PITER_LOGS_TRACES_AWS_CHECK.md) |
| 12 | [PITER_POST_AWS_READONLY_LOCAL_VERIFICATION.md](./PITER_POST_AWS_READONLY_LOCAL_VERIFICATION.md) |
| 13 | This document |

---

## Final decision matrix

| Option | When |
|--------|------|
| **A. Ready with current AWS** | If demo uses `retrieve_and_generate` only and notifications stay preview/mock |
| **B. Ready with KB path; agent alignment next** | **← Current recommendation** |
| **C. Needs AWS fixes before demo** | If you require agent-default path or live SMS to unverified numbers |
| **D. Do not demo** | Not applicable — no blocking failures found |

**Stopped after report. No AWS mutations, commits, or deployments performed.**
