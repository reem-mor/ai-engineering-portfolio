# PITER AWS Mutation Final Report

**Date:** 2026-06-08  
**Decision:** **A — Demo-ready on both direct KB and agent paths; enterprise alignment substantially complete**

---

## 1. AWS changes performed

| # | Change | Status |
|---|--------|--------|
| 1 | Deploy/update Lambda `piter-escalation` (mock-safe env) | **Done** |
| 2 | Add action group `piter-escalation` + S3 OpenAPI + Lambda permission | **Done** |
| 3 | Publish guardrail `rti921amc6u3` v2; attach to agent | **Done** |
| 4 | Add `bedrock:ApplyGuardrail` to agent IAM role | **Done** |
| 5 | Sync agent instruction from `AGENT_INSTRUCTION` | **Done** |
| 6 | Disable legacy `incidentiq-ops` on live alias | **Done** |
| 7 | Prepare agent; route alias `live` to new version | **Done** (v6) |
| 8 | CloudWatch log retention 14d on Lambda log groups | **Done** |
| 9 | Delete temporary alias `piter-live-snapshot` | **Done** |

No SNS/SES messages sent. No S3 deletions. No KB deletion.

---

## 2. Resources modified

- Lambda: `piter-escalation`
- IAM: `incidentiq-agent-role/incidentiq-agent-resource`, `incidentiq-lambda-role` (+ existing notifications policy)
- S3: `agent/piter-escalation/openapi_schema.yaml`
- Bedrock Agent: `HH4YGSLZUE` DRAFT + versions 4–6
- Bedrock Alias: `O2EM03R4R3` (`live`)
- Guardrail: `rti921amc6u3` v2
- CloudWatch: retention on 5 Lambda log groups

---

## 3. Before / after

| Item | Before | After |
|------|--------|-------|
| Alias routing | v3 | **v6** |
| `piter-escalation` | Not deployed | Lambda + action group **ENABLED** |
| Guardrail on live path | Not attached | **v2 attached** |
| `incidentiq-ops` | ENABLED | **DISABLED** on live |
| Agent invoke | Working (no guardrail) | Working with guardrail + ApplyGuardrail IAM |

---

## 4. Agent alias / version

| Alias | ID | Version |
|-------|-----|---------|
| `live` | `O2EM03R4R3` | **6** |

Intermediate versions 4–5 created during snapshot testing; v5 alias test resource deleted.

---

## 5. KB association

KB `RBTJM6NIG9` **ENABLED** on DRAFT and v6.

---

## 6. Guardrail

`rti921amc6u3` version **2**, status **READY**, attached to live agent version.

---

## 7. Lambda / action groups (live v6)

| Group | State |
|-------|--------|
| `iiq-context` | ENABLED |
| `iiq-correlate` | ENABLED |
| `iiq-similar` | ENABLED |
| `piter-escalation` | ENABLED |
| `incidentiq-ops` | DISABLED |
| `incidentiq-ops-test` | DISABLED |

---

## 8. SNS / SES

Configured; **mock/preview only** during validation. SMS sandbox remains.

---

## 9. IAM

Agent role updated for guardrail + escalation Lambda. No destructive IAM changes.

---

## 10. CloudWatch

14-day retention on tool Lambda log groups. No secrets in sampled logs.

---

## 11. Tests run

| Test | Result |
|------|--------|
| `python -m pytest` | **271/271 PASS** |
| `python scripts/verify_live_demo.py` | **29/29 PASS** |
| `RAG_BACKEND=agent` + `agent_smoke_test.py` | **7/7 PASS** |
| `scripts/agent_p1_smoke.py` | Grounded P1 response; section headers vary by model formatting |
| Docker `http://localhost:8080/health` | **200** |

---

## 12. Direct KB path

Default `.env` / `.env.example`: `RAG_BACKEND=retrieve_and_generate` — **29/29** live demo checks.

---

## 13. Agent path

`RAG_BACKEND=agent` with alias `O2EM03R4R3` — **7/7** smoke, citations and guardrail active.

---

## 14. Docker

Container `piter-aiops` healthy on port 8080.

---

## 15. Rollback instructions

1. **Alias:** `aws bedrock-agent update-agent-alias ... --routing-configuration agentVersion=3` (if v3 still exists)
2. **Re-enable ops:** set `incidentiq-ops` to ENABLED on DRAFT, prepare, new version
3. **Guardrail:** remove `guardrailConfiguration` from agent, prepare, new version
4. **Lambda:** disable action group; function can remain

Preflight snapshots: [`PITER_AWS_MUTATION_PREFLIGHT.md`](PITER_AWS_MUTATION_PREFLIGHT.md), [`aws_snapshot/`](aws_snapshot/)

---

## 16. Remaining gaps

| Gap | Priority |
|-----|----------|
| Rename `iiq-*` → `piter-*` in AWS console | P3 |
| Re-run KB ingestion after corpus changes | P3 |
| SNS SMS sandbox exit / SES production | P3 |
| Delete disabled `incidentiq-ops-test` group | P4 |
| Stricter IAM for admin user | P4 |

---

## 17. Demo readiness

**Yes.** Use `retrieve_and_generate` for the graded live demo script; show one scene with `RAG_BACKEND=agent` for Bedrock Agent + guardrail + `piter-escalation` mock path.

---

## 18. Presentation talking points

1. PITER pipeline on Alert Storm (399 alerts → one P1)
2. Citations from KB runbooks (postgres, bet-service, escalation policy)
3. Enrichment tools (`iiq-*`) + new **`piter-escalation`** preview (masked, no live send)
4. Guardrail blocks off-topic and dangerous ops requests
5. Session memory follow-up (“Who do I escalate to?”)
6. Local fallback when Bedrock unavailable
7. Notifications gated: mock by default; live requires token + allowlist

---

## Local artifacts

- Orchestrator: [`scripts/setup_piter_aws_mutations.py`](../../scripts/setup_piter_aws_mutations.py)
- P1 smoke: [`scripts/agent_p1_smoke.py`](../../scripts/agent_p1_smoke.py)
- Phase reports: [`docs/review/`](./)
