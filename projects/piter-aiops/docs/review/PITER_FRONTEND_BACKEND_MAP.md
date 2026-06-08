# PITER Frontend / Backend Route Map

## HTTP routes (`app/routes.py` + `app/spa.py`)

| Route | Method | Handler | Serves | Used by |
|-------|--------|---------|--------|---------|
| `/` | GET | `home()` | React SPA if `app/static/spa/index.html` exists; else Jinja `index.html` | Browser default |
| `/console` | GET | `console()` | Jinja `console.html` standalone demo | `verify_live_demo`, grading, Docker default URL in compose comment |
| `/ask` | GET | 405 | — | Legacy |
| `/ask` | POST | `ask()` | HTMX partial or JSON RAG | Legacy `index.html` HTMX |
| `/workflow/triage` | POST | HTMX workflow | `_workflow_result.html` | Legacy MVP workflow |
| `/api/workflow/triage` | POST | JSON workflow | RAG-only payload (`build_workflow_payload`) | SPA workflow demo path |
| `/api/bootstrap` | GET | JSON | CSRF token, examples, notification settings, execution hints | SPA `fetchBootstrap` |
| `/api/alert-stream` | GET | JSON | Storm summary + rows | SPA storm panel |
| `/api/demo-alert` | GET | JSON | `p1_demo_alert()` | Console + SPA storm |
| `/api/triage` | POST | JSON | Full PITER card (`run_triage`) | **Primary** console + SPA |
| `/api/follow-up` | POST | JSON | `run_follow_up` | Chat follow-up |
| `/api/escalation/notify` | POST | JSON | SNS/SES dispatch (gated) | SPA escalation button |
| `/api/kb/manifest` | GET | JSON | KB sections for UI | SPA knowledge panel |
| `/health` | GET | JSON | Liveness | Docker/K8s/verify scripts |
| `/documents/upload` | POST | JSON | S3 + optional KB ingestion | SPA upload |
| `/assets/<path>` | GET | static | Vite bundle assets | SPA |
| `/<path>` | GET | SPA fallback | `index.html` for client routes | React router |

## Frontend implementations

| Implementation | Path | Status |
|----------------|------|--------|
| **React SPA (primary)** | `frontend/src/App.tsx` → build → `app/static/spa/` | Active when build present |
| **Jinja console** | `app/templates/console.html` | Required for 29/29 verify |
| **HTMX landing** | `app/templates/index.html`, `_live_kb.html` | Fallback when `FORCE_LEGACY_UI` or no SPA build |

## API client

- SPA: `frontend/src/lib/api.ts` — `runTriageCard`, `followUp`, `fetchBootstrap`, `uploadDocument`
- Console: inline `fetch` in `console.html`

## Duplicate / dead UI risks

| Item | Assessment |
|------|------------|
| SPA `triageAlert` → `/api/workflow/triage` | Second triage stack (RAG-only); not full PITER card |
| Buttons labeled mock/preview | Check `App.tsx` bootstrap flags — most gated by `notification_mode` |
| `/console` vs `/` | Intentional dual surface until SPA fully certified |

## verify_live_demo.py dependencies

- `GET /console` (200)
- `POST /api/triage` with postgres + bet-service scenarios
- `POST /api/follow-up` with session_id
- Does **not** require SPA route `/` (uses test client against Flask app directly)
