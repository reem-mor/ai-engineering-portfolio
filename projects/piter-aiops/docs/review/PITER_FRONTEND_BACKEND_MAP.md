# PITER AiOps — Frontend / Backend Map

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Route map (`app/routes.py`, `app/spa.py`)

| Route | Method | Serves | Notes |
| ----- | ------ | ------ | ----- |
| `/` | GET | SPA `index.html` (or Jinja if `FORCE_LEGACY_UI`) | `_bootstrap_context()` |
| `/api/bootstrap` | GET | JSON | examples, alerts, config, CSRF token, execution-mode hint, notification settings |
| `/ask` | POST | JSON/HTML | core Q&A → `_handle_ask()` (3-tier RAG + fallback) |
| `/workflow/triage` | POST | HTML | Jinja workflow card |
| `/api/workflow/triage` | POST | JSON | workflow triage + optional `session_id` |
| `/console` | GET | Jinja `console.html` | self-contained local-first demo console |
| `/api/alert-stream` | GET | JSON | deterministic alert-storm metadata + rows |
| `/api/kb/manifest` | GET | JSON | KB document list for SPA |
| `/api/demo-alert` | GET | JSON | canned Postgres CPU P2 alert |
| `/api/triage` | POST | JSON | free-form alert → triage card → `run_triage()` |
| `/api/escalation/notify` | POST | JSON | live escalation gate (token + allowlist + severity) |
| `/api/follow-up` | POST | JSON | session-memory follow-up → `run_follow_up()` |
| `/health` | GET | JSON | `?deep=1` checks S3 + Bedrock config |
| `/documents/upload` | POST | HTML/JSON | S3 upload + optional KB ingestion |
| `/assets/<path>` | GET | static | SPA bundle assets |
| `/<path:path>` | GET | SPA fallback | unmatched → `index.html` |

## UI layers
| Layer | Location | Status |
| ----- | -------- | ------ |
| React/Vite SPA (authoritative UI) | `frontend/src/**` → built to `app/static/spa/` | Active; served at `/` and SPA fallback |
| Jinja console (fallback / parity) | `app/templates/console.html` + partials | Active at `/console`; part of the 29 verify checks |
| Jinja base/index | `app/templates/base.html`, `index.html` | Legacy fallback when `FORCE_LEGACY_UI=true` |

## SPA build pipeline
- Source: `frontend/src` (React 19, TanStack Router, Radix/shadcn, Tailwind 4).
- `npm run build` (Vite) → outputs to `../app/static/spa` (hashed assets + `index.html`).
- Flask `app/spa.py` serves the built bundle; `spa_enabled()` gates SPA vs Jinja.
- **Do not hand-edit** `app/static/spa/*`; edit `frontend/src` and rebuild.

## Strategy (per plan)
- React/Vite SPA is the main authoritative UI.
- **Keep `/console`** until the SPA independently passes all 29 verify checks (it is itself a check).
- Keep Jinja fallback templates (offline/no-JS resilience).
- No duplicate UI removed in this pass (additive/polish only).

## Build verification (this session)
`npm ci && npm run build` → clean; assets deterministic (only CRLF→LF on `index.html`, reverted to
keep the bundle byte-identical to the committed copy until the dedicated UI commit).
