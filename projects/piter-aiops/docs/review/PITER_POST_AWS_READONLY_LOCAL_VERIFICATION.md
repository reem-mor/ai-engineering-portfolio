# PITER Post-AWS Readonly Local Verification

**Audit date:** 2026-06-08  
**After:** Phases 1–11 read-only AWS audit (no mutations)

## pytest

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops
.\.venv\Scripts\python.exe -m pytest -q
```

| Metric | Result |
|--------|--------|
| Tests collected | **271** |
| Outcome | **All passed** |

## verify_live_demo.py

```powershell
.\.venv\Scripts\python.exe scripts\verify_live_demo.py
```

| Phase | Result |
|-------|--------|
| A — Live AWS (`RAG_BACKEND=retrieve_and_generate`) | **15/15 PASS** |
| B — Simulated AWS-down → local fallback | **14/14 PASS** |
| **Total** | **29/29 PASS** |

Highlights Phase A:

- Grounded answer with postgres CPU runbook citations
- Tools: correlate_deployments, owner/escalation, business impact, similar incidents
- Session memory on follow-up

## Docker (daemon running)

```powershell
docker compose config    # valid
docker compose ps        # piter-aiops Up (healthy)
Invoke-WebRequest http://localhost:8080/health  # {"status":"ok"}
```

| Check | Result |
|-------|--------|
| Compose config | Valid |
| Container status | **Healthy** on port 8080 |
| Health endpoint | **OK** |

## invoke_agent (supplemental, not in verify_live_demo default path)

Separate smoke with `RAG_BACKEND=agent`: **PASS** (~27s latency). See `PITER_INVOKE_AGENT_SMOKE_CHECK.md`.

## Regression vs user baseline

| Baseline (user reported) | This audit |
|--------------------------|------------|
| git clean | **Confirmed** |
| pytest 271 | **271 pass** |
| verify_live_demo 29/29 | **29/29** |
| Live Bedrock RAG | **Working** |
| Local fallback | **Working** |

**Verdict:** Local baseline remains healthy after read-only AWS audit.
