# Bet Service Outage Runbook (GIB-UKGC demo scenario)

When bet-service reports 100% error rate in GIB-UKGC:

1. Confirm the alert is not a false positive from canary traffic.
2. Check recent deployments on bet-service and bet-api within the last 6 hours.
3. Inspect postgres connection pool saturation and kafka-settlement consumer lag.
4. If a deploy correlates with the onset, initiate rollback per deployment rollback procedure.
5. Validate error rate recovery and settlement backlog for 10 minutes.

Regulated-market P1 incidents require escalation to betting-oncall. Use mock notification preview only in demo environments.
