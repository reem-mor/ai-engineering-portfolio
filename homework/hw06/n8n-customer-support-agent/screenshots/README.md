# Submission Screenshots

Captured evidence for HW06, taken from the live n8n editor
(`https://reemmor.app.n8n.cloud`, workflow id `b5mJup2hTkC3G2Ge`) and the
connected Gmail and Slack accounts. The top-level
[README screenshots table](../README.md#screenshots) and
[submission checklist](../README.md#submission-checklist-per-the-docx) link to
each file.

| File | What it shows |
|---|---|
| `01_full_workflow.png` | Annotated architecture diagram of the whole project: Chat Trigger -> Guardrails -> Agent (+ models, memory) -> Gmail + Slack tools and the Blocked Response branch, plus the defense-in-depth explanation, model tiering, the four live test results, and the edge-case matrix (A-E). |
| `02_agent_configuration.png` | `Customer Support Agent` node open: the system prompt (rules 1-9), the `$('Customer Chat').item.json.chatInput` expression, and the test case 1 run (login help, no tools used). |
| `03_guardrails_config.png` | `Input Guardrails` node open: jailbreak threshold 0.7, the investment keyword list, and the topical alignment prompt; shows test case 4 routed to the fail branch (jailbreak 0.95 / topical 0.98). |
| `04_gmail_emails_sent.png` | Gmail inbox listing the `Billing Support Request` emails produced by billing runs. |
| `05_gmail_email_format.png` | A single billing email opened: subject with the AI summary, the verbatim customer message, and the auto-escalation footer with timestamp. |
| `06_slack_escalation.png` | The Block Kit alert posted to the support channel for a billing run: Summary / Type / Status / customer message / timestamp. |

## Mapping to the docx requirements

- Full workflow + explanation -> `01_full_workflow.png`
- AI Agent configuration -> `02_agent_configuration.png`
- Guardrails configuration -> `03_guardrails_config.png`
- Gmail sent proof -> `04_gmail_emails_sent.png` + `05_gmail_email_format.png`
- (Bonus) Slack posted proof -> `06_slack_escalation.png`

All shots are full-window PNGs with no credentials or secrets visible in frame.
