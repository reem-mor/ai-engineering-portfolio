---
title: "Severity and escalation policy"
doc_type: "policy"
services: []
environments: ["NJ-DGE", "GIB-UKGC", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3", "P4"]
tags: ["severity", "escalation", "notifications"]
last_updated: "2026-06-06"
author: "PITER AiOps"
version: "1.0"
---

# Severity and Escalation Policy

## Severity Guidance

- `P1`: customer-facing outage, data integrity risk, payment impact, or regulated-market exposure.
- `P2`: significant degradation, partial outage, or single-market impact.
- `P3`: recoverable degradation with limited customer impact.
- `P4`: operational noise or maintenance follow-up.

## Notification Safety

Notifications default to mock mode. Live SNS or SES dispatch is blocked unless
all confirmation, allowlist, severity, and idempotency checks pass.

Do not store real phone numbers or personal email addresses in Git, incoming
data, Lambda source, OpenAPI examples, tests, screenshots, README, or KB files.

## Escalation Preview

The KB may explain escalation policy. Recipient resolution and current routing
must come from `piter-escalation` and its approved structured data sources.
