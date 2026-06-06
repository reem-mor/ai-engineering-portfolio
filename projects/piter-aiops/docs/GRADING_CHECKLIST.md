# Grading checklist

Course and demo acceptance criteria for PITER AiOps. See also the detailed checklist in [`GRADING_CHECKLIST.md`](GRADING_CHECKLIST.md).

## Demo reliability

- [ ] `py -3.12 -m pytest` passes offline
- [ ] `py -3.12 scripts/verify_live_demo.py` — 29/29
- [ ] `py -3.12 scripts/verify_spa_demo.py` — 36/36
- [ ] Docker health `200` on `:8080`
- [ ] SPA shows **399 alert storm** label from live API data

## RAG and tools

- [ ] Triage card returns citations and `recommended_steps`
- [ ] Enrichment: deploy correlation, owner, impact, similar incidents
- [ ] Storm P1 (`bet-service` / `GIB-UKGC`) returns owner and similar incidents
- [ ] Follow-up sets `memory_used: true`
- [ ] Local fallback works when Bedrock KB id is invalid

## Safety

- [ ] Notifications in mock/preview mode by default
- [ ] No real PII in repo datasets or KB
- [ ] `/console` preserved until `PITER_CONSOLE_REDIRECT_SPA=true`

## Documentation

- [ ] README describes implemented vs mocked
- [ ] Architecture documents agent / KB / local paths
- [ ] `docs/mcp.md` explains action groups vs MCP
