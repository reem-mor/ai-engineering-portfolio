---
title: "Regulated market environments"
doc_type: "environment"
services: []
environments: ["NJ-DGE", "GIB-UKGC", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3", "P4"]
tags: ["environment", "regulated-markets", "routing"]
last_updated: "2026-06-06"
author: "PITER AiOps"
version: "1.0"
---

# Regulated Market Environments

## When to use

Use this reference when an alert, deployment, or incident includes an environment
code and the responder needs to understand business and regulatory exposure.

## Environment Map

| Environment | Market meaning | Operational note |
|---|---|---|
| `NJ-DGE` | New Jersey regulated gaming | Treat wallet, bet, auth, and replication P1/P2 incidents as regulatory exposure. |
| `GIB-UKGC` | Gibraltar / UKGC regulated gaming | Escalate prolonged betting, wallet, and auth impact quickly. |
| `MGM` | MGM partner environment | Coordinate partner-facing status updates for P1 impact. |
| `MIRAGE` | Mirage partner environment | Partner impact is usually lower volume but still customer-facing. |

## Freshness Boundary

The Knowledge Base may describe what an environment means, but current deploys,
current on-call rotation, current alerts, and live notification recipients must
come from structured data or Lambda tools.
