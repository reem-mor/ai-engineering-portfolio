# RB-010: Deployment Rollback Procedure

**Runbook ID:** RB-010  
**Severity:** Procedure (applies to any P1/P2 caused by a deploy)  
**Applies to:** Any service in `service_catalog.json` across all environments  
**Alert name:** Triggered by another runbook when `correlate_deployments` finds a suspect deploy

## Symptoms

- An incident timeline starts shortly after a deployment.
- `correlate_deployments` returns a likely suspect deploy within the window.
- Error rate / latency regressed immediately after the rollout.

## Detection checks

1. Confirm the suspect deploy: service, version, commit, deploy time.
2. Verify the regression started after (not before) the deploy time.
3. Check whether the deploy included a database migration (changes rollback safety).
4. Confirm the previous known-good version is still available.

## Recommended steps

1. Notify the owning team and incident channel before rolling back.
2. Roll back to the previous known-good version for the affected service only.
3. If the deploy included a forward-only migration, do NOT auto-rollback the DB —
   involve the DBA and consider a fix-forward instead.
4. Re-run health checks and the failing scenario after rollback.
5. Keep the bad artifact for the post-incident review.

## Dangerous actions warning

- Do NOT roll back a service whose deploy included an irreversible (forward-only)
  database migration without DBA review — this can corrupt or lose data.
- Do NOT roll back unrelated services in the same window.
- Never auto-execute a production rollback without human approval.

## Escalation path

- **Tier-1:** Steps 1–2 for a clean, migration-free rollback.
- **Owning team on-call:** Any rollback involving a database migration.
- **P1:** If rollback does not restore service within the SLA window, escalate.

## Business / regulatory impact

A controlled rollback restores service fastest; an unsafe migration rollback can
create a data-integrity incident with regulatory reporting consequences.

## Example commands

```bash
# Roll a Kubernetes deployment back to the previous revision
kubectl rollout undo deployment/<service> -n <namespace>
kubectl rollout status deployment/<service> -n <namespace>
```

## Related documents

- `deployment_rollback_sop.docx` — formal SOP (binary format for compliance archive)

## Tags / services

`deploy`, `rollback`, `migration`, `kubernetes`, `change-management`, `correlate_deployments`
