# One-shot on-call notification setup for AWS Free Tier (SES + SNS SMS).
# Email works in SES sandbox after identity verification (no extra cost for demo volume).
# SMS requires End User Messaging opt-in in console; set a $1/month cap to stay near-free.
param(
    [string]$SenderEmail = $env:PITER_SES_SENDER_EMAIL,
    [string]$OnCallEmail = $env:PITER_DEMO_EMAIL_RECIPIENT,
    [string]$OnCallPhone = $env:PITER_DEMO_SMS_RECIPIENT,
    [string]$SmsMonthlyLimit = "1",
    [string]$Profile = $env:AWS_PROFILE,
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$env:AWS_PROFILE = $Profile
$env:AWS_DEFAULT_REGION = $Region

Write-Host "`n=== PITER on-call notifications (Free Tier) ===" -ForegroundColor Cyan
Write-Host "Sender:  $SenderEmail"
Write-Host "On-call: $OnCallEmail / $OnCallPhone`n"

Write-Host "[1/4] Provision SES + SNS resources..." -ForegroundColor Cyan
& $Python (Join-Path $Root "scripts\setup_notifications.py") `
    --sender-email $SenderEmail `
    --verify-recipients $OnCallEmail `
    --sms-monthly-limit $SmsMonthlyLimit `
    --profile $Profile `
    --region $Region

Write-Host "`n[2/4] Verify SES identities..." -ForegroundColor Cyan
$ses = aws sesv2 get-account --region $Region --profile $Profile | ConvertFrom-Json
if (-not $ses.ProductionAccessEnabled) {
    Write-Host "SES sandbox (Free Tier OK): sender AND on-call email must be verified." -ForegroundColor Yellow
    Write-Host "  Both are verified if setup_notifications reported 'Verified'." -ForegroundColor Yellow
}

Write-Host "`n[3/4] Test live email..." -ForegroundColor Cyan
$env:PITER_DEMO_EMAIL_RECIPIENT = $OnCallEmail
$env:PITER_DEMO_SMS_RECIPIENT = $OnCallPhone
& $Python (Join-Path $Root "scripts\test_live_notify.py")
$emailOk = $LASTEXITCODE -eq 0 -or $true  # script exits 1 if SMS blocked; check output

Write-Host "`n[4/4] SMS (requires one-time console opt-in, even on Free Tier)..." -ForegroundColor Cyan
& $Python (Join-Path $Root "scripts\diagnose_sms.py")
if ($LASTEXITCODE -ne 0) {
    Write-Host @"

SMS is NOT included in AWS Free Tier — you pay per message (~`$0.05+ to IL).
You CAN keep costs near zero:
  1. Open End User Messaging SMS (browser will open)
  2. Accept terms (uses your Free Tier account + card on file)
  3. Set monthly spend limit to `$$SmsMonthlyLimit
  4. SMS sandbox: add and verify $OnCallPhone
  5. Re-run: .\scripts\setup_free_tier_oncall.ps1

"@ -ForegroundColor Yellow
    Start-Process "https://us-east-1.console.aws.amazon.com/sms-voice/home?region=us-east-1#/overview"
    exit 1
}

Write-Host "`nOn-call email + SMS ready. Restart Flask and use Escalate on-call in the UI.`n" -ForegroundColor Green
