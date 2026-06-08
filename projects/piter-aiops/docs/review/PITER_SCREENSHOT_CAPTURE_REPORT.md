# PITER Screenshot Capture Report

**Date:** 2026-06-08  
**Output:** `screenshots/final/`

## SPA enterprise demo (`capture_final_demo.mjs`)

| # | File | Content |
|---|------|---------|
| 1 | `01_dashboard.png` | Dashboard |
| 2 | `02_investigations_table.png` | Investigations |
| 3 | `03_alert_storm_running.png` | Alert storm streaming |
| 4 | `04_p1_detected.png` | P1 candidate |
| 5 | `05_investigation_detail_triage.png` | Post–Run PITER analysis |
| 6 | `06_rag_citations.png` | Citations panel |
| 7 | `07_lambda_mcp_tools.png` | MCP / Lambda Tools |
| 8 | `08_memory_followup_context.png` | Context Memory |
| 9 | `09_escalation_preview.png` | Escalation modal |
| 10 | `10_post_mortem_summary.png` | Storm / resolution view |
| 11 | `11_knowledge_base.png` | Knowledge Base |
| 12 | `12_upload_document_flow.png` | Upload |
| 13 | `13_architecture_settings.png` | Architecture |
| 14 | `13b_settings_aws_status.png` | Settings / AWS status |
| 15 | `14_tests_passing.png` | pytest summary |
| 16 | `14b_live_demo_checks.png` | verify_live_demo 29/29 |
| 17 | `15_docker_running.png` | Docker ps |

## Legacy console (`capture_console_demo.mjs`)

Additional clips under `screenshots/console_demo/` (01–12) including citations, follow-up memory, mobile.

## Hygiene

- PITER AiOps branding visible
- No full phone numbers or emails in captures
- No secrets in terminal screenshots

## Commands

```powershell
cd projects/piter-aiops/scripts
npm ci
npx playwright install chromium
node capture_final_demo.mjs
node capture_console_demo.mjs
node render_docker_status.mjs
```
