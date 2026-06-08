# PITER Frontend ↔ Backend Integration Check

**Date:** 2026-06-08  
**Primary UI:** React SPA at `/` (`frontend/src/App.tsx`)

## Route map

| Route | Backend | Status |
|-------|---------|--------|
| `/` | SPA static + `/api/bootstrap` | Live |
| `/console` | `console.html` or SPA redirect | Live (legacy HTML default) |
| `/ask` | POST RAG Q&A | Live |
| `/api/bootstrap` | Config + alert stream summary | Live |
| `/api/triage` | Analyze incident / triage card | Live |
| `/api/follow-up` | Session memory follow-up | Live |
| `/api/alert-stream` | Storm dataset + P1 trigger | Live |
| `/api/kb/manifest` | KB document list | Live |
| `/documents/upload` | Local/demo upload | Live |
| `/api/escalation/notify` | Gated SNS/SES | Live (mock/preview default) |
| `/health` | Health probe | Live |

## Button audit

| Control | Wiring | Label / behavior |
|---------|--------|------------------|
| Start / Pause / Reset storm | Client simulation over `/api/alert-stream` data | Live demo UI |
| Run PITER analysis | `POST /api/triage` | Live |
| Follow-up / Ask Agent | `POST /api/follow-up` or `/ask` | Live |
| Upload document | `POST /documents/upload` | Live (local index; KB sync separate) |
| Escalate on-call (SMS/email) | Opens modal → `POST /api/escalation/notify` | Gated |
| Dashboard filters | Disabled | **Demo filter — display only** |
| Investigations In Process / Resolve / Escalate | Local React state | **Demo UI — local status only** |
| Citation panel (empty) | Placeholder | **Example — run Analyze Incident for live citations** |

## Fixes applied this session

- Stable escalation `idempotency_key`: `{incidentId}:{channel}` (was random UUID per click)
- Alert timeline text: **400** deterministic alerts (matches `alert_stream.csv`)
- Investigation table actions documented via `title` tooltips
