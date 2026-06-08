# PITER Live Validation — Preflight

**Date:** 2026-06-08  
**Scope:** `projects/piter-aiops` only  
**Branch:** `main` @ `7d2174b` (+ local demo polish)

## Preflight commands

| Check | Result |
|-------|--------|
| Working directory | `C:\dev\amdocs-ai-course\projects\piter-aiops` |
| Git branch | `main` |
| Working tree | Clean at mission start; demo polish changes staged at end |
| `python -m pytest` | **271 passed** |
| `python scripts/verify_live_demo.py` | **29/29 passed** |
| `python scripts/verify_spa_demo.py` | **36/36 passed** |
| Docker `/health` | **200** `{"status":"ok"}` |

## Baseline protected

- Bedrock RAG (retrieve_and_generate) live path verified in Phase A of `verify_live_demo.py`
- Local fallback verified in Phase B
- Session memory + follow-up verified
- SPA enabled at `/`; legacy console at `/console`

## Notes

- Python **3.12** required for test run (`C:\Users\reemm\AppData\Local\Programs\Python\Python312\python.exe`)
- Do not commit `.env` or expose notification recipients in docs/screenshots
