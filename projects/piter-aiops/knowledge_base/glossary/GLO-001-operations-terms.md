---
title: "PITER AiOps operations glossary"
doc_type: "glossary"
services: []
environments: ["NJ-DGE", "GIB-UKGC", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3", "P4"]
tags: ["glossary", "operations", "rag"]
last_updated: "2026-06-06"
author: "Re'em Mor"
version: "1.0"
---

# PITER AiOps Operations Glossary

## Terms

- **Bedrock Agent**: Primary orchestration path for PITER AiOps when live AWS mode is enabled.
- **Direct Bedrock KB**: Fallback Bedrock retrieval path using retrieve-and-generate.
- **Local fallback**: Local deterministic retrieval path used when Bedrock is unavailable.
- **Citation**: Source reference returned with a grounded RAG answer.
- **Enrichment tool**: Lambda-backed or local tool that adds deploy, service, impact, or incident context.
- **Mock notification**: Safe preview path that does not send SMS or email.
- **Confirmed live dispatch**: Future SNS/SES path allowed only after explicit confirmation, allowlist, severity, and idempotency checks.
