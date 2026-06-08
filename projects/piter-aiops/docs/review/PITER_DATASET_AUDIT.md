# PITER Dataset Audit (`data/source/`)

**Canonical folder:** `data/source/`  
**Audit date:** 2026-06-08

## File inventory

| File | Rows/entries | Status |
|------|----------------|--------|
| `alert_stream.csv` | 400 | PASS |
| `alerts.csv` | 8 | PASS (curated subset) |
| `deploys.csv` | 61 | PASS |
| `service_owners.csv` | 8 services | PASS |
| `on_call_schedule.csv` | 24 | PASS |
| `past_incidents.csv` | 35 | PASS |
| `business_impact.json` | 3 environments | PARTIAL — not per-service |
| `priority_matrix.json` | P1–P4 thresholds | PASS |
| `escalation_policies.json` | 3 policies | PASS |

## P1 / storm trigger

| Check | Result |
|-------|--------|
| Deterministic row count | 400 |
| Exactly one `is_trigger=true` | **YES** — `ALT-2026-06-10-0251`, `bet-service` |
| Exactly one `severity=P1` | **YES** (same row) |
| Note | Column is `severity`, not `priority` |

## Validation (automated)

`tests/test_source_data.py` verifies:

- Required files exist
- No raw email/phone patterns in source CSVs
- Runbook references resolve to `knowledge_base/runbooks/` or `sample_documents/`
- Generated alerts include `ALT-DEMO-P1-001`
- Deploy correlation for bet-service (`DEP-2026-06-0610-001` in `deploys.csv`)

## Cross-file consistency

| Check | Status |
|-------|--------|
| Services in alerts ⊆ owners | PASS for source services; **postgres demo** only in legacy `agent_data` |
| Business impact keys | Maps `GIB-UKGC`, `NJ-DGE`, `MGM` — not every service row |
| Environment codes | `GIB-UKGC`, `NJ-DGE`, `MGM`, `MIRAGE` — **mismatch** with `incidentiq-ops` Lambda (`GIB`, `NJ`) |
| Money values non-negative | PASS in sampled files |
| ISO timestamps | PASS in tests |

## Generators

| Script | Notes |
|--------|-------|
| `scripts/enrich_incident_csvs.py` | Project-relative paths |
| `data/source/README.md` | Documents schema |

No `/home/claude` hardcoded paths found in dataset generators (spot-check).

## Gaps

1. Expand `business_impact.json` to cover all 8 services or document 3-env model.
2. Add `postgres` to `service_owners.csv` for default demo parity with analysis pipeline.
3. Align `incidentiq-ops` env codes with compound environment names.
