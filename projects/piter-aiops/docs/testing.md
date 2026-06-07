# Testing

## Offline unit tests

```bash
cd projects/piter-aiops
python -m pytest
```

Key suites:

| File | Covers |
|---|---|
| `test_alert_stream_api.py` | `/api/alert-stream`, bootstrap summary |
| `test_knowledge_base.py` | YAML front matter including RB runbooks |
| `test_source_data.py` | 390–400 alert bound, PII-free CSV |
| `test_piter_lambdas.py` | Four piter-* tools + escalation safety |
| `test_spa_mode.py` | SPA assets, bootstrap fields, 399 labels |

## Live demo verification

```bash
python scripts/verify_live_demo.py
python scripts/verify_spa_demo.py
```

Phase A requires `USE_BEDROCK=true` in `.env`. Phase B forces invalid KB id → local fallback.

## Frontend build

```bash
cd frontend && npm ci && npm run build
```

Output lands in `app/static/spa/`. Never hand-edit hashed assets.

See also [`TESTING.md`](TESTING.md) for historical notes.
