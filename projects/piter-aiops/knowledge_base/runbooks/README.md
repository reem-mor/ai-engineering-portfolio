---
title: "PITER AiOps runbook index"
doc_type: "runbook"
services: []
environments: ["NJ-DGE", "GIB-UKGC", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3", "P4"]
tags: ["index", "runbooks"]
last_updated: "2026-06-06"
author: "PITER AiOps"
version: "1.0"
---

# PITER AiOps Runbook Index

The files in this folder are the authoritative Markdown runbook set for the
organized PITER AiOps Knowledge Base.

The current live demo still uses `data/sample_documents` as the verified Bedrock
and local fallback corpus. This folder is the migration target for the later KB
sync phase; do not remove `data/sample_documents` until live RAG, citations,
enrichment, memory, and fallback all pass against the replacement.

## Runbook Set

- `RB-001-api-gateway-5xx-spike.md`
- `RB-002-auth-login-failures.md`
- `RB-003-settlement-backlog.md`
- `RB-004-postgres-replica-lag.md`
- `RB-005-connection-pool-exhaustion.md`
- `RB-006-promotions-engine-latency.md`
- `RB-007-postgres-cpu-high.md`
- `RB-008-redis-token-store-degradation.md`
- `RB-009-kafka-consumer-lag.md`
- `RB-010-deployment-rollback.md`

Each runbook includes YAML front matter for future Bedrock metadata filtering.
