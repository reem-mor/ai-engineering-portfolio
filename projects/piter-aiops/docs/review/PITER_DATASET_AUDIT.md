# PITER AiOps — Dataset Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07
- **Canonical folder:** `data/source/`

## Required datasets — all present
| File | Rows / size | Notes |
| ---- | ----------- | ----- |
| `alert_stream.csv` | **399 data rows** | streaming storm; `is_trigger` + `seconds_offset` |
| `alerts.csv` | 26 | historical snapshot |
| `deploys.csv` | 44 | deploy correlation, `rollback_available` |
| `service_owners.csv` | 7 | ownership + escalation routing |
| `on_call_schedule.csv` | 19 | names/roles (no raw private contacts) |
| `past_incidents.csv` | 35 | root cause, resolution, `mttr_min` |
| `business_impact.json` | — | SLA/customer impact profiles |
| `priority_matrix.json` | — | severity/impact scoring factors |
| `escalation_policies.json` | — | notify-immediately by severity (no real phone/email) |

## Validation results
| Check | Result |
| ----- | ------ |
| Unique IDs | PASS |
| ISO timestamps | PASS |
| Valid service names | PASS (synthetic catalog) |
| Valid environments | PASS (NJ-DGE, GIB-UKGC, MGM, MIRAGE …) |
| Priorities P1–P4 | PASS |
| Non-negative financials | PASS |
| No duplicate rows | PASS |
| **One deterministic P1 trigger** | **PASS** — exactly 1 `is_trigger`=true and 1 `P1` row: `ALT-DEMO-P1-001` |
| Realistic business-impact values | PASS |
| Similar incidents connect to demo | PASS (Postgres CPU scenario matches `past_incidents`) |
| On-call uses names/roles | PASS |
| No credentials / phone / email in `data/source` | PASS (PII lives only in docs/scripts — fixed in Commit 2) |
| Valid UTF-8 | PASS |
| Deterministic generators | PASS (`scripts/generate_demo_data.py`, `generate_alert_stream.py`) |
| No hardcoded `/home/...` paths in generators | PASS |
| `--output` support | PASS (generators accept output paths) |

## Alert storm count (Phase 6 decision)
`alert_stream.csv` = **399 deterministic alerts**. Decision: **Option A** — keep 399 and label the
UI/docs "Simulated alert storm — 399 deterministic alerts". No fake numbers.

## Status: PASS — datasets professional, validated, deterministic, PII-free.
