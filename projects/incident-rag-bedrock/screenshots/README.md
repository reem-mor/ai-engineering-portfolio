# Screenshots

Submission proof captures. Drop the PNGs alongside this file using the exact filenames below.

| # | Filename | What it must show |
|---|---|---|
| 01 | `01_bedrock_kb_overview.png` | Bedrock → Knowledge bases → detail page for `incident-ops-kb` |
| 02 | `02_bedrock_kb_data_source_synced.png` | Data source row with **Status: Available** after Sync |
| 03 | `03_bedrock_model_access_granted.png` | Bedrock → Model access — Claude 3 Haiku = **Access granted** |
| 04 | `04_ec2_instance_running.png` | EC2 → Instances — your instance with public DNS visible |
| 05 | `05_security_group_rules.png` | Inbound rules: 22/tcp from your IP, 80/tcp from anywhere |
| 06 | `06_docker_ps_on_ec2.png` | SSH session showing `docker ps` → `Up (healthy)` |
| 07 | `07_app_homepage_public.png` | Browser at `http://<EC2_PUBLIC_DNS>/` showing the IncidentIQ UI |
| 08 | `08_app_question_and_answer.png` | A real grounded answer with citation cards |
| 09 | `09_app_refusal_or_low_confidence.png` | An irrelevant question producing the amber "No matching context" card |
| 10 | `10_cleanup_console.png` | Empty Bedrock / EC2 / OpenSearch console after teardown |
