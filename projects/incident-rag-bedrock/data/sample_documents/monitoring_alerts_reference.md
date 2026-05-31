# Monitoring & Alert Reference

A single source of truth for what each alert means, what the on-call
engineer should do first, and which runbook to consult.

## P1 — page immediately

| Alert name | Condition | First action | Runbook |
|---|---|---|---|
| `AuthGlobalErrorRateCritical` | login error rate > 25% for 5m | Roll back if recent deploy; else escalate | `auth_service_runbook.md` |
| `PaymentGatewayDown` | 100% non-2xx for 2m on `/charge` | Failover to backup PSP | `payment_service_latency_runbook.txt` |
| `DatabasePrimaryUnreachable` | health probe fails 3× | Promote standby; involve DBA | `database_connectivity_runbook.md` |
| `ApiGateway5xxStorm` | 5xx > 10% for 3m | Check upstream service map | `api_gateway_5xx_runbook.txt` |

## P2 — page within 15 minutes

| Alert | Condition | First action |
|---|---|---|
| `AuthMfaProviderDegraded` | MFA delivery success < 95% for 10m | Failover to backup provider |
| `ReplicationLagHigh` | Postgres lag > 60s for 10m | Remove replica from LB |
| `DiskUsageHigh` | any volume > 85% for 15m | Rotate logs / extend volume |

## P3 — handle during business hours

Anything labelled `severity:warn` in Prometheus. These do **not** page
out of hours unless they roll up into a P1/P2.

## Silence policy

Silences must always include a Jira ticket reference and an expiry of
at most 24 hours. Open-ended silences are forbidden.
