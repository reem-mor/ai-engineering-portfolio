# PITER AiOps Screenshots

Use `screenshots/final/` for the mid-project submission and live-demo README.
These captures match the current React dashboard, Flask API flow, PITER memory
screen, Knowledge Base view, tool results, and Docker/test proof.

## Final Submission Set

| File | Shows |
|------|-------|
| `final/01_dashboard.png` | Current React dashboard |
| `final/02_investigations_table.png` | Investigation queue |
| `final/03_alert_storm_running.png` | Alert storm running |
| `final/04_p1_detected.png` | P1 detected and stream paused |
| `final/05_investigation_detail_triage.png` | Structured PITER triage |
| `final/06_rag_citations.png` | Knowledge Base citations |
| `final/07_lambda_mcp_tools.png` | Four Lambda/MCP-style tools |
| `final/08_memory_followup_context.png` | Session memory follow-up |
| `final/09_escalation_preview.png` | Safe escalation preview |
| `final/10_post_mortem_summary.png` | Resolution/post-mortem view |
| `final/11_knowledge_base.png` | Knowledge Base document list |
| `final/12_upload_document_flow.png` | Upload flow |
| `final/13_architecture_settings.png` | Architecture view |
| `final/13b_settings_aws_status.png` | AWS/status settings |
| `final/14_tests_passing.png` | Test proof |
| `final/14b_live_demo_checks.png` | Live demo verification proof |
| `final/15_docker_running.png` | Docker container proof |

## Legacy Captures

Root-level PNGs, `console_demo/`, `extras/`, and `archive/` are historical
captures from earlier UI or AWS proof flows. Keep them for audit if useful, but
do not use them as the primary README or live-submission screenshots unless the
instructor specifically asks for those older proof filenames.

## Regenerate

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops
docker compose up --build -d
.\.venv\Scripts\python.exe scripts\verify_live_demo.py
cd scripts
npm ci
node capture_final_demo.mjs
```
