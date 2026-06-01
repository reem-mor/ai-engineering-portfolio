# Tier-1 vs Escalation Decision Guide

Use this guide when deciding whether to resolve an alert at Tier-1 or escalate to a specialist team.

## Resolve at Tier-1 when

1. The runbook has deterministic, safe actions (check health, tail logs, scale workers, cancel long queries with DBA-approved SQL).
2. Customer impact is low or isolated (single pod, non-production, P3 alert).
3. A recent deploy clearly caused the issue and rollback SOP allows immediate rollback.
4. The alert matches a known pattern in `alerts_last_3mo.json` with documented resolution.

## Escalate when

1. Customer impact is high — checkout, auth, or payment flows degraded (P1/P2).
2. Data loss, security breach, payment processing failure, or production-wide outage is possible.
3. The runbook explicitly requires DBA, DevOps platform, backend owner, or security on-call.
4. Tier-1 actions did not improve the signal within the runbook time box (typically 15 minutes).
5. You are unsure — escalate early with prepared notes (queries run, deploy IDs, log excerpts).

## Document every action

- Alert ID, time, actions taken, and outcome in the incident ticket.
- Link the runbook and citations used from the Knowledge Base.
- Note who was paged and when if escalated.

## Related documents

- `escalation_policy.pdf` — P1–P4 definitions and paging chain
- `on_call_handoff_checklist.pdf` — shift handoff requirements
