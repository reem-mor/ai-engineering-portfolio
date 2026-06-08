---
title: "Business Impact Matrix"
doc_type: "policy"
services: "auth-service, payment-service, api-gateway, redis-token-store, customer-db"
environments: "production, GIB-UKGC, NJ-DGE"
severity_applicable: "P1,P2,P3,P4"
tags: "business impact, priority, sla, revenue"
last_updated: "2026-06-08"
author: "PITER AiOps"
version: "1.0"
---

# Business Impact Matrix

Use this matrix to explain customer, revenue, SLA, and regulatory impact in incident responses.

## Tier-0 Services

- Auth-service: blocks login and all authenticated journeys. P1 if most users cannot log in.
- Payment-service: direct transaction revenue impact and compliance follow-up.
- API Gateway: can block all customer traffic even when backends are healthy.
- Customer database and Redis token store: dependency failures can cascade into auth, wallet, and payments.

## Priority Heuristics

- P1: broad customer-facing outage, high revenue risk, or regulated-market exposure.
- P2: major degradation, partial outage, or high-impact single market.
- P3: recoverable degradation with limited customer impact.
- P4: operational noise with no customer impact.

## Explanation Template

State the affected service, users or market, estimated revenue exposure, SLA risk, regulatory risk, and the next mitigation step.
