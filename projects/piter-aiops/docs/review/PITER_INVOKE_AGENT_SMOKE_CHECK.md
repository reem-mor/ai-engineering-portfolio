# PITER AWS Phase 5 — invoke_agent Smoke Check

**Audit date:** 2026-06-08  
**Method:** Local `BedrockAgentClient.ask()` → `boto3` `bedrock-agent-runtime.invoke_agent`  
**Override:** `RAG_BACKEND=agent` (`.env` default is `retrieve_and_generate`)

## Test prompt

```
P1 incident detected:
Service: bet-service
Environment: GIB-UKGC
Title: CRITICAL: bet-service nodes unresponsive - 100% error rate
Affected users: 32000
Ask PITER AiOps to return Priority, Investigation findings, Triage plan,
Escalation recommendation, Resolution plan, Business impact, Sources, and Confidence.
```

## Results

| Check | Result |
|-------|--------|
| invoke_agent ran | **Yes** |
| Returned text | **Yes** (6371 chars) |
| KB citations | **Yes** — 3 citations |
| Tool / action group usage | **Yes** — `enrichment.tools` populated |
| Session ID | **Yes** — `piter-aws-readiness-7d6f6d41` |
| PITER format sections | **All present** (Priority, Investigation, Triage, Escalation, Resolution, Business impact, Sources, Confidence) |
| Hallucinated contacts avoided | **Mostly** — references on-call paths from policy/runbook; cites INC-2026-* from enrichment (verify against `incident_history.csv`) |
| Confidence / uncertainty | **Yes** — section present; includes "Option A: High Confidence" language |
| Latency | **~27.2s** (27199 ms reported) |
| Errors | **None** |

## Top citations

1. `runbook_bet_service_outage.md`
2. `incident_history.csv`
3. `runbook_wallet_transaction_failures.md`

## Enrichment

- `enrichment.tools` key present (deployments, similar incidents, context tools invoked via agent orchestration).

## Answer quality notes

- Correctly classified **P1** with GIB-UKGC regulatory context.
- Triage plan is ordered and cites runbooks (RB-010, RB-011, RB-012).
- Escalation names **Primary Betting Core On-Call** and **GIB-UKGC P1 Compliance Officer** — should match KB/policy, not invented phone numbers.
- Resolution paths require **human approval** before rollback/restart — aligns with safety rules.

## Comparison to live demo path

| Path | Config | Status |
|------|--------|--------|
| `retrieve_and_generate` | Current `.env` | **Working** — `verify_live_demo.py` 29/29 PASS |
| `invoke_agent` | Requires `RAG_BACKEND=agent` | **Working** — this smoke test PASS |

## If invoke_agent had failed (reference)

Not applicable this run. Typical fixes (require AWS mutation):

- Re-prepare agent after action group changes
- Fix agent role `bedrock:InvokeModel` / inference profile permissions
- Verify alias points to prepared version

## Command used

```powershell
$env:AWS_PROFILE='reemmor'
$env:RAG_BACKEND='agent'
# BedrockAgentClient.ask() via project venv — same path as scripts/agent_smoke_test.py
```

**No AWS resources were modified.**
