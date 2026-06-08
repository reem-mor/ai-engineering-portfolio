# PITER Alert Storm Live Check

**Date:** 2026-06-08

## Dataset

- Source: `data/source/alert_stream.csv`
- **Row count: 400** (verified via CSV parse)
- UI label: **Simulated alert storm — 400 deterministic alerts**

## Deterministic P1

- Service: **bet-service**
- Environment: **GIB-UKGC**
- Exactly one P1 trigger in stream metadata (`/api/alert-stream`, bootstrap)

## Storm behavior (SPA)

1. Start alert storm → client-side stream animation  
2. Noise grouping / duplicate suppression → counts from bootstrap summary  
3. P1 detected → stream pauses; P1 candidate card shown  
4. Run PITER analysis → `POST /api/triage` with P1 payload  
5. Escalation preview → modal (mock/preview notification mode)

## Data-backed enrichment (post-triage)

| Field | Source file |
|-------|-------------|
| Priority matrix | `data/source/priority_matrix.json` |
| Escalation | `data/source/escalation_policies.json` |
| Owners | `data/source/service_owners.csv` |
| Deployments | `data/source/deploys.csv` |
| Business impact | `data/source/business_impact.json` |
| Similar incidents | `data/source/past_incidents.csv` |

## Verification

`verify_spa_demo.py`: alert stream 390–400, P1 trigger bet-service — **PASS**
