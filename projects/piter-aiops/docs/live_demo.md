# Live demo

## Baseline checks

```bash
python -m pytest
python scripts/verify_live_demo.py    # 29/29 — uses /console + /api/triage
python scripts/verify_spa_demo.py   # API-only parity for React SPA
```

## Recording flow (SPA)

1. Open `http://localhost:8080/` → **Alert Storm Demo**
2. **Start alert storm** — UI shows *Simulated alert storm (399 alerts)* from `/api/alert-stream`
3. **Run PITER workflow** — `POST /api/triage` with P1 bet-service payload
4. Agent panel — follow-up via `POST /api/follow-up` (session memory)
5. Legacy console remains at `/console` until `PITER_CONSOLE_REDIRECT_SPA=true`

## Postgres scenario (verify script)

`verify_live_demo.py` uses a postgres CPU P2 scenario for Bedrock/local fallback proof.
The SPA storm demo uses the CSV P1 bet-service trigger — both share the same triage API contract.

## Docker

```bash
docker compose up -d --build
curl http://localhost:8080/health
```

## Before enabling SPA console redirect

1. `verify_spa_demo.py` passes all checks
2. Set `PITER_CONSOLE_REDIRECT_SPA=true` in `.env`
3. Re-run both verify scripts
