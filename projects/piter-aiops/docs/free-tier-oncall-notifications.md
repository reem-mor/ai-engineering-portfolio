# On-call notifications on AWS Free Tier

PITER escalation uses **SES (email)** and **SNS (SMS)**. Both work on a Free Tier account; SMS is not free per message, but demo volume with a **$1/month cap** stays near zero.

## What works today on your account

| Channel | Free Tier | Your status |
|---------|-----------|-------------|
| **Email (SES)** | Sandbox: 200 emails/day; verify sender + each recipient | **Ready** — `sender@example.com` → `oncall@example.com` |
| **SMS (SNS)** | No free SMS; ~$0.05+ per message; **$1/month cap** recommended | **Blocked** until End User Messaging SMS is enabled in console |

Your `.env` is already correct for live dispatch:

```env
PITER_NOTIFICATION_MODE=live
PITER_ENABLE_LIVE_DISPATCH=true
PITER_NOTIFICATION_ALLOWLIST=+10000000000,sender@example.com,oncall@example.com
PITER_SES_SENDER_EMAIL=sender@example.com
PITER_DEMO_EMAIL_RECIPIENT=oncall@example.com
PITER_DEMO_SMS_RECIPIENT=+10000000000
```

Use IAM user **`admin-reem`** (profile `reemmor`) — **not root**.

Run setup once — it creates the managed policy **and attaches it** to `admin-reem`, `IncidentRagBedrockEC2Role`, and `incidentiq-lambda-role`:

```powershell
python scripts/setup_notifications.py --sender-email sender@example.com --verify-recipients oncall@example.com --profile reemmor
```

## One-command setup

```powershell
cd projects\piter-aiops
.\scripts\setup_free_tier_oncall.ps1
```

This provisions SNS topic + SES config, verifies identities, tests email, and opens the SMS console if needed.

## Email only (works now, $0)

1. Run Alert Storm → **Escalate on-call**
2. Enter confirmation token: `piter-demo-2026`
3. Click **Send email**

CLI test:

```powershell
python scripts/test_live_notify.py
```

Email should show `"sent": true`.

## SMS (one-time console step, ~$1 cap)

AWS cannot enable SMS via API on first use. In the console:

1. [End User Messaging SMS](https://us-east-1.console.aws.amazon.com/sms-voice/home?region=us-east-1#/overview) — accept terms
2. **Text messaging preferences** — monthly spend limit **$1** (enough for demos)
3. **SMS sandbox** — add `+10000000000`, enter OTP from your phone
4. Re-run:

```powershell
python scripts/fix_sms_subscription.py --otp <code-from-sms>
python scripts/diagnose_sms.py          # must show "ready": true
python scripts/test_live_notify.py
```

Then **Send SMS** in the escalation modal works.

## Free Tier limits (what to expect)

- **SES sandbox**: only verified addresses (`sender@example.com`, `oncall@example.com`). No production access needed for your demo.
- **SES cost**: effectively $0 at demo volume (within 200/day sandbox quota).
- **SMS cost**: not in Free Tier; each alert is a few cents. The $1 monthly cap prevents surprises.
- **No root user** required; `Administrators` group IAM user is sufficient.

## IAM for EC2/Lambda

`setup_notifications.py` attaches `PITER-AiOps-Notifications` automatically. Manual attach only if you skipped that step:

```powershell
aws iam attach-role-policy `
  --role-name IncidentRagBedrockEC2Role `
  --policy-arn arn:aws:iam::329597159579:policy/PITER-AiOps-Notifications `
  --profile reemmor
```

Local dev uses `admin-reem` via `AWS_PROFILE=reemmor` — policy is attached to that user as well.
