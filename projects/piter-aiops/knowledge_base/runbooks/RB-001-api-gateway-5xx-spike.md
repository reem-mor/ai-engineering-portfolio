---
title: "API Gateway 5xx spike"
doc_type: "runbook"
services: ["api-gateway"]
environments: ["NJ-DGE", "GIB-UKGC"]
severity_applicable: ["P1", "P2"]
tags: ["edge", "5xx", "gateway"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-001: API Gateway 5xx Spike

**Severity:** P1 (customer-facing) / P2 (single client)
**Applies to:** `api-gateway` edge tier in `NJ-DGE`, `GIB`
**Alert name:** `ApiGateway5xxHigh` — 5xx rate > 2% over 5 minutes

## Symptoms

- Edge dashboards show 5xx ratio climbing above 2% on `api-gateway`.
- Downstream `checkout-api` and `auth-api` report upstream 502/503/504 errors.
- Latency p99 rises before the error rate spikes.

## Detection checks

1. Confirm the alert scope: which route, stage, and environment.
2. Check `api-gateway` integration latency vs. backend health.
3. Inspect recent deploys with the `correlate_deployments` tool.
4. Verify the custom domain TLS certificate is valid (expired certs cause total 5xx).
5. Check WAF rules for a false-positive block.

## Recommended steps

1. Identify whether errors are gateway-origin (5xx at edge) or backend-origin (upstream timeouts).
2. If a recent deploy correlates, prepare a rollback (see RB-010).
3. Scale the impacted backend if it is saturated, not the gateway.
4. If a WAF rule is over-blocking, move it to count mode for the affected client only.
5. Re-test the failing route after each change before declaring recovery.

## Dangerous actions warning

- Do NOT disable the WAF globally to clear false positives — narrow the rule instead.
- Do NOT bump rate limits to "unlimited"; this can amplify a downstream outage.

## Escalation path

- **Tier-1:** Steps 1–4 when a single route or client is affected.
- **edge-oncall:** Gateway-origin 5xx above 2% for 10 minutes.
- **P1:** Checkout or auth blocked company-wide → page `edge-l2 -> edge-oncall`.

## Business / regulatory impact

Public API unavailability directly blocks deposits and bets in regulated
markets. Sustained 5xx in `NJ-DGE` carries SLA and regulatory-reporting risk.

## Example commands

```bash
# Tail gateway error logs for a route
aws logs tail /aws/apigateway/edge --since 10m --filter-pattern '"status":5'
# Check certificate expiry
echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -dates
```

## Tags / services

`api-gateway`, `edge`, `5xx`, `latency`, `waf`, `tls`
