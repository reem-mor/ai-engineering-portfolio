# Escalation Policy

## Severity Levels

### Critical

Use Critical when one or more of the following is true:

- All users are affected.
- Production is down.
- Payment processing is failing or duplicate charge risk exists.
- Security incident is suspected.
- Data loss or database outage is suspected.

Escalate immediately to the incident commander, service owner, backend team, and relevant domain team.

### High

Use High when:

- Many users are affected.
- Production login is failing.
- API Gateway 5xx errors are high.
- A major service is unavailable.
- A recent deployment caused visible production impact.

Escalate to the service owner and backend team. Open an incident channel and start impact assessment.

### Medium

Use Medium when:

- Some users are affected.
- Latency is degraded.
- A non-critical workflow is partially failing.
- The issue is in staging but may affect production soon.

Escalate to the owning team during working hours unless impact grows.

### Low

Use Low when:

- Warning only.
- No user impact.
- Cosmetic issue.
- Informational alert.

Create a ticket and monitor.

## Communication Expectations

For High and Critical incidents, provide updates every 15 minutes. Include impact, suspected cause, current action, owner, and next update time.
