# Monitoring Alerts Reference

## Alert Naming Convention

Alerts follow this format: `service.environment.metric.condition`. Example: `auth.production.error_rate.high`.

## Auth Alerts

- `auth.production.error_rate.high`: High login API error rate.
- `auth.production.login_failure.spike`: Many users cannot log in.
- `auth.production.jwt.validation_errors`: JWT validation errors detected.

## Payment Alerts

- `payment.production.latency.high`: Payment-service p95 latency is above threshold.
- `payment.production.provider.timeout`: External payment provider timeout rate is high.
- `payment.production.queue.backlog`: Payment retry queue is growing.

## Database Alerts

- `database.production.locks.high`: Blocking database locks detected.
- `database.production.query_latency.high`: Database query latency is high.
- `database.production.connections.exhausted`: Connection pool is exhausted.

## API Gateway Alerts

- `gateway.production.5xx.high`: API Gateway 5xx error rate is high.
- `gateway.production.upstream.unavailable`: Upstream service is unavailable.
- `gateway.production.rate_limit.spike`: Rate limit errors increased.

## Severity Mapping

Critical severity applies to all users affected, payment risk, data loss, security incidents, or production down.
High severity applies to many users affected, production login failure, major 5xx spikes, or unavailable services.
Medium severity applies to partial degradation, latency, or staging issues.
Low severity applies to warnings with no user impact.

## First Response Checklist

1. Confirm alert time and affected service.
2. Check if the alert is production or staging.
3. Check recent deployments.
4. Check dashboard metrics.
5. Check logs.
6. Escalate according to severity.
