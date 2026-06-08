# PITER Legacy Action Group Cleanup

**Date:** 2026-06-08  
**Live alias:** `O2EM03R4R3` → version **6**

## Before

| Action group | State (v3/v4) |
|--------------|---------------|
| `iiq-context` | ENABLED |
| `iiq-correlate` | ENABLED |
| `iiq-similar` | ENABLED |
| `incidentiq-ops` | ENABLED |
| `incidentiq-ops-test` | DISABLED |
| `piter-escalation` | Added v4+ |

## After (v6)

| Action group | State |
|--------------|--------|
| `iiq-context` | ENABLED (kept for demo reliability) |
| `iiq-correlate` | ENABLED |
| `iiq-similar` | ENABLED |
| **`incidentiq-ops`** | **DISABLED** |
| `incidentiq-ops-test` | DISABLED |
| **`piter-escalation`** | **ENABLED** |

## Rationale

- `piter-escalation` replaces legacy ops escalation/notification path for PITER naming
- `iiq-*` groups retained — still map to working enrichment Lambdas; no PITER-renamed Lambda swap yet
- `incidentiq-ops` disabled only after agent smoke **7/7** on v6

## Validation after disable

| Check | Result |
|-------|--------|
| `verify_live_demo.py` | **29/29** |
| `agent_smoke_test.py` | **7/7** |
| `pytest` | **271/271** |

## Rollback

```powershell
python scripts/setup_piter_aws_mutations.py --skip-guardrail
# Then manually re-enable incidentiq-ops via update_agent_action_group actionGroupState=ENABLED
# prepare_agent + update_agent_alias (no routing pin)
```

Lambda functions were **not deleted**.
