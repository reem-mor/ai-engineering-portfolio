# PITER AiOps — Repository Inventory

Read-only audit generated 2026-06-06. Excludes `.git`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`, and other generated caches.

**Total tracked files:** 381

| Path | Type | Purpose | Referenced by | Generated? | Required? | Recommendation |
| ---- | ---- | ------- | ------------- | ---------- | --------- | -------------- |
| `.dockerignore` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `.ec2_instance_id.txt` | Temporary/debug file | Local AWS/debug artifact | None | Yes | No | Delete candidate (after approval) |
| `.env` | Secret risk | Local env / credentials | Runtime | No | No | Keep gitignored; never commit |
| `.env.example` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `.env.production` | Secret risk | Local env / credentials | Runtime | No | No | Keep gitignored; never commit |
| `.gitignore` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `.sg_id.txt` | Temporary/debug file | Local AWS/debug artifact | None | Yes | No | Delete candidate (after approval) |
| `.ssh/amdocs-course-key.pem` | Secret risk | Local env / credentials | Runtime | No | No | Keep gitignored; never commit |
| `.vscode/extensions.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `action_groups/iiq-context/data/deploys.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/data/impact_matrix.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/data/service_catalog.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/enrichment_tools.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/events/demo_impact.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/events/demo_owner.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/lambda_function.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-context/openapi_schema.yaml` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/data/deploys.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/data/impact_matrix.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/data/service_catalog.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/enrichment_tools.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/events/demo_correlate.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/lambda_function.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-correlate/openapi_schema.yaml` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/data/deploys.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/data/impact_matrix.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/data/incident_history.csv` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/data/service_catalog.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/enrichment_tools.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/events/demo_similar.json` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/lambda_function.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/iiq-similar/openapi_schema.yaml` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/incidentiq-ops/lambda_function.py` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/incidentiq-ops/openapi_schema.yaml` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `action_groups/incidentiq-ops/README.md` | Required runtime source | Lambda action group | setup_enrichment_lambdas.py | No | Yes | Keep |
| `app/__init__.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/bedrock_agent_client.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/bedrock_client.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/config.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/data/example_questions.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/data/workflow_alerts.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/data_loader.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/enrichment_tools.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/errors.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/local_agent.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/rag_factory.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/routes.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/services/__init__.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/services/data_access.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/services/local_rag.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/services/session_memory.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/services/tool_router.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/services/triage_service.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/spa.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/static/css/styles.css` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/static/img/logo.svg` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/static/js/app.js` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/static/spa/assets/index-DTvgJLUv.js` | Generated but required for deployment | Vite production bundle | Flask spa.py, Dockerfile | Yes | Yes (until rebuild) | Keep; rebuild via npm run build |
| `app/static/spa/assets/index-gnDErQsM.css` | Generated but required for deployment | Vite production bundle | Flask spa.py, Dockerfile | Yes | Yes (until rebuild) | Keep; rebuild via npm run build |
| `app/static/spa/index.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_answer.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_architecture.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_deliverables.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_document_upload.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_flow.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_hero.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_live_kb.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_mvp_workflow.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_problem.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_stack.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_system_guide.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_upload_result.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/_workflow_result.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/base.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/console.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/templates/index.html` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `app/text_utils.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/upload_service.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/upload_validators.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/validators.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/workflow.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app/workflow_impact.py` | Required runtime source | Flask app module | routes, tests, rag_factory | No | Yes | Keep |
| `app.py` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `data/agent_data/deploys.csv` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `data/agent_data/impact_matrix.csv` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `data/agent_data/service_catalog.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `data/demo_qa_expected.md` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `data/external_status.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `data/sample_documents/alerts_last_3mo.json` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/api_gateway_5xx_runbook.txt` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/auth_service_runbook.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/database_connectivity_runbook.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/deployment_rollback_sop.docx` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/escalation_policy.pdf` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/incident_history.csv` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/monitoring_alerts_reference.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/on_call_handoff_checklist.pdf` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/payment_service_latency_runbook.txt` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/postmortem_2024_07.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/postmortem_template.docx` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/README.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_auth_login.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_checkout_5xx.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_connection_pool.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_db_cpu.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_deployment_rollback.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_kafka_consumer_lag.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_promotions_engine_latency.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_queue_lag.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_redis_token_store.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_replication_lag.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/runbook_settlement.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `data/sample_documents/tier1_escalation_guide.md` | Required runtime source | KB corpus (local + S3) | local_rag, KB sync | No | Yes | Keep |
| `docker-compose.yml` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `Dockerfile` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `docs/architecture.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/bedrock_action_group_setup.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/bedrock_agent_setup.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/bedrock_kb_setup.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/cleanup_checklist.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/cleanup_log.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/code_review.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/DEPLOY_STATUS.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/development_environment.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/ec2_deployment.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/edge_cases.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/GRADING_CHECKLIST.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/INVOKEAGENT_VERIFICATION.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/LIVE_DEMO_CHECKLIST.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/MCP_PATH.json` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/MCP_PATH.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/PHASE0_AUDIT.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/presentation_outline.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/PRODUCTION_REVIEW.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/READONLY_VERIFICATION.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/review/_gen_inventory.py` | Required documentation | Audit output | This review | No | Yes | Keep |
| `docs/SUBMISSION_CHECKLIST.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/teacher_submission_email.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/TEARDOWN.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `docs/UPGRADE_STATUS.md` | Required documentation | Project docs | README links | No | Mostly yes | Keep; archive stale after approval |
| `evaluation/agent_ops_smoke_results.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/agent_smoke_results.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/CORPUS_RECONCILIATION.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/live_demo_aws_state.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/live_smoke_summary.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/pytest_output.txt` | Temporary/debug file | Local AWS/debug artifact | None | Yes | No | Delete candidate (after approval) |
| `evaluation/qa_showcase.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/smoke_results.md` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `evaluation/test_questions.json` | Required test | Eval/smoke artifacts | smoke scripts | Mixed | Yes | Keep |
| `frontend/.gitignore` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/.lovable/project.json` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/.prettierignore` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/.prettierrc` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/bun.lock` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/bunfig.toml` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/components.json` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/eslint.config.js` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/index.html` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/package-lock.json` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/package.json` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/App.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/AppTopBar.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/CodeBlock.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/DemoDashboard.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/EnrichmentPanel.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/FormattedAnswer.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/StepPipeline.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/accordion.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/alert-dialog.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/alert.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/aspect-ratio.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/avatar.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/badge.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/breadcrumb.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/button.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/calendar.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/card.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/carousel.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/chart.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/checkbox.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/collapsible.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/command.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/context-menu.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/dialog.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/drawer.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/dropdown-menu.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/form.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/hover-card.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/input-otp.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/input.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/label.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/menubar.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/navigation-menu.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/pagination.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/popover.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/progress.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/radio-group.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/resizable.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/scroll-area.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/select.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/separator.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/sheet.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/sidebar.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/skeleton.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/slider.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/sonner.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/switch.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/table.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/tabs.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/textarea.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/toggle-group.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/toggle.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/components/ui/tooltip.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/context/bootstrap.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/context/demo-tour.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/context/workflow-session.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/hooks/use-mobile.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/answer-format.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/api/example.functions.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/api.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/config.server.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/error-capture.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/error-page.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/rag.functions.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/utils.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/lib/workflow-utils.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/main.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/router.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/routes/__root.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/routes/index.tsx` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/routes/README.md` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/routeTree.gen.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/server.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/start.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/styles.css` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/src/types/rag.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/tsconfig.json` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `frontend/vite.config.ts` | Required runtime source | React SPA source | Docker build stage | No | Yes | Keep |
| `infra/agent_resource_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/agent_trust_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/bedrock_kb_s3_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/bedrock_kb_s3_policy_live.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/ec2_inline_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/ec2_trust_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/ec2_user_data.sh` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/ec2_user_data_demo.sh` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/ec2_user_data_docker_only.sh` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/ec2_user_data_ecr.sh` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/iam_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/iam_policy_ec2_resolved.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/kb_retrieve_smoke.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/lambda_execution_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/lambda_trust_policy.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/README.md` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/update_datasource_piter.json` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `infra/upload_docs_to_s3.sh` | Required configuration | AWS/IaC helpers | setup scripts | No | Yes | Keep |
| `knowledge_base/runbooks/RB-001-api-gateway-5xx-spike.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-002-auth-login-failures.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-003-settlement-backlog.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-004-postgres-replica-lag.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-005-connection-pool-exhaustion.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-006-promotions-engine-latency.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-007-postgres-cpu-high.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-008-redis-token-store-degradation.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-009-kafka-consumer-lag.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/RB-010-deployment-rollback.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `knowledge_base/runbooks/README.md` | Required runtime source | Docker-packaged runbooks | Dockerfile COPY | No | Yes | Keep |
| `lambda-out.json` | Temporary/debug file | Local AWS/debug artifact | None | Yes | No | Delete candidate (after approval) |
| `piter_architecture.mermaid` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `PLAN.md` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `pytest.ini` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `README.md` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `requirements.txt` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
| `screenshots/01_agent.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/01_bedrock_kb_overview.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/02_bedrock_kb_data_source_synced.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/02_kb_sync.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/03_bedrock_model_access_granted.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/03_mcp.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/04_ec2_instance_running.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/04_lambdas.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/05_s3.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/05_security_group_rules.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/06_docker_ps_on_ec2.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/06_ec2.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/07_app_home.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/07_app_homepage_public.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/08_app_question_and_answer.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/08_qa.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/08b_app_citations_expanded.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/09_app_refusal_or_low_confidence.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/09_memory_followup.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/10_cleanup_console.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/10_mobile.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/11_docker_ps.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/11_pytest_passed.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/12_kb_smoke_evaluation.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/12_tests.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/13_mvp_workflow.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/14_architecture.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/15_document_upload_success.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/16_document_upload_validation.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/17_document_upload_type_rejected.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/18_dataset_corpus.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/19_sample_questions_answers.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/archive/20_codex_local_verification.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/archive/partA_home_1440.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/01_home.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/02_demo_alert.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/03_loading.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/04_triage_card.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/05_citations.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/06_owner_escalation.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/07_business_impact.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/08_similar_incidents.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/09_followup_memory.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/10_mobile.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/11_pytest.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/console_demo/12_smoke_results.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/deployment_validation.md` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/extras/partA_answer_1440.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/extras/partA_answer_390.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/extras/partA_answer_768.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/extras/partA_answer_expanded_1440.png` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `screenshots/README.md` | Required documentation | Submission screenshots | README | No | Optional | Keep if referenced |
| `scripts/agent_smoke_test.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/browser_audit.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/build_corpus.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/capture_agent_submission.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_aws_proof.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_cleanup_proof.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_console_demo.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_ec2_proof.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_ec2_submission.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_partA.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_public_app.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_screenshots.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_spa_screenshots.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/capture_terminal_proof.mjs` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/ensure_agent_alias.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/kb_reconciliation_retrieval_check.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/kb_smoke_test.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/launch_ec2_demo.ps1` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/package-lock.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/package.json` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/redeploy_lambdas.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/setup_action_group.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/setup_agentcore_gateway.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/setup_bedrock_agent.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/setup_enrichment_lambdas.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/verify.ps1` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `scripts/verify_console_demo.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/verify_e2e.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `scripts/verify_live_demo.py` | Required configuration | Ops/setup script | README, docs | No | Yes | Keep |
| `TESTING.md` | Needs verification | Misc project file | TBD | Unknown | Verify | Review manually |
| `tests/conftest.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_agent.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_agent_client.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_api_routes.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_bedrock_agent_client.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_bedrock_client.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_config.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_data_access.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_data_corpus.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_enrichment_tools.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_errors.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_flask_routes.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_health.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_lambda_action_handler.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_rag.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_rag_factory.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_routes.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_spa_mode.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_text_utils.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_tools.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_upload_routes.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_upload_service.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_upload_validators.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_validators.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `tests/test_workflow_impact.py` | Required test | Pytest module | pytest | No | Yes | Keep |
| `wsgi.py` | Required configuration | Project infra | Docker/pytest | No | Yes | Keep |
