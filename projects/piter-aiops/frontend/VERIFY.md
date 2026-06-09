# PITER AiOps SPA — Verification (F2-R)

Manual click-test and automated gates for `frontend-redesign` (enterprise layout + demo choreography).

## Automated gates

| Check | Command | Expected |
|-------|---------|----------|
| Production build | `cd frontend && npm run build` | `app/static/spa/index.html` + `assets/index-*.js` |
| Backend tests | `pytest -q` (project root) | **297+** passed |
| Deep health | `curl http://localhost:8080/api/health?deep=1` | JSON `status` + `checks` |

## Serve locally

**Backend** (pick one):

```powershell
cd projects\piter-aiops
.\scripts\run-local.ps1
```

Or: `.\.venv\Scripts\python.exe -m flask --app wsgi:app run -p 8080 --host=127.0.0.1`

Open `http://localhost:8080/` for the built SPA, or run Vite for hot reload:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173/` (proxies `/api` to :8080). See [`docs/LOCAL_DEV.md`](../docs/LOCAL_DEV.md).

## F2-R click-test matrix

- [ ] **Logo → Home** — Click PITER logo from every nav page; lands on Operations Dashboard.
- [ ] **Nav** — Operations, Agent Analytics, History, Analyzer, System.
- [ ] **Start Alert Stream** — DEMO tag, alert table fills, KPIs tick, decisions feed updates.
- [ ] **P1 popup (~20s)** — Analyze / Escalate / Ask Agent / Continue Live; no overlapping modals.
- [ ] **Reset Demo** — Visible in demo mode; clears state for second run.
- [ ] **Alert row Ask agent** — Opens dock with context.
- [ ] **History toggles** — Alerts and Incidents views with search/filter.
- [ ] **System tools** — All four metrics forms; escalation shows PREVIEW ONLY.
- [ ] **Chat dock** — Collapse to rail, expand full panel, session selector load+continue.
- [ ] **Escalation mock** — POST returns `sent: false` or `mode: mock`; toast shows receipt; incident Escalated.

## Demo choreography (run twice)

1. Start Alert Stream → wait for P1 modal.
2. Test each action once per rehearsal (Analyze, Escalate confirm, Ask Agent, Continue Live).
3. Let stream complete or Reset Demo between runs.

## Docker (optional)

```powershell
docker compose up --build
curl http://localhost:8080/api/health?deep=1
```

## Screenshots (presenter report)

Capture: Home idle, Home mid-storm, P1 popup, analysis view, escalation modal + receipt, Agent Analytics, History (both toggles), full-panel chat.

## Rollback

Pre-rebuild SPA: commit `7e98a82` (`pre-frontend-rebuild snapshot`).
