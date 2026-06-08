# PITER Analyze Incident Output Check

**Date:** 2026-06-08

## P1 scenario (bet-service / GIB-UKGC)

Triggered via SPA **Run PITER analysis** → `POST /api/triage` with P1 demo payload.

## Required structure (triage card)

| Section | Present |
|---------|---------|
| Priority + rationale | Yes — from priority matrix + symptoms |
| Investigation findings | Yes — grounded answer text |
| Triage plan / recommended steps | Yes — `recommended_steps` |
| Escalation recommendation | Yes — owner + escalation chain |
| Resolution plan | Yes — runbook-aligned steps |
| Business impact | Yes — from `business_impact.json` |
| Sources / citations | Yes — Bedrock KB citations (live) |
| Confidence / uncertainty | Yes — grounded flag + latency/mode pill |

## P1 field checks (no hallucination)

Values must trace to CSV/JSON sources — enforced by enrichment services + tests:

- Service owner / on-call — `service_owners.csv`
- Recent deployment — `deploys.csv`
- Rollback availability — deploy + runbook context
- Regulatory exposure — business impact JSON
- Similar incidents — `past_incidents.csv`

## Legacy console capture

`screenshots/console_demo/04_triage_card.png` — mode pill **bedrock**, citations + owner + impact sections clipped.

## API verification

`verify_live_demo.py` postgres P2 scenario: grounded citations, 4 tools, follow-up memory — **29/29 PASS**
