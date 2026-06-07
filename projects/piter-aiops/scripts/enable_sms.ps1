# Enable AWS End User Messaging SMS for PITER (interactive helper).
# CLI cannot opt in — first visit must happen in the AWS Console while logged in.
param(
    [string]$Phone = $env:PITER_DEMO_SMS_RECIPIENT,
    [string]$MonthlyLimit = "10",
    [string]$Profile = $env:AWS_PROFILE,
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not $Phone) { $Phone = "+972526775754" }
if (-not $Profile) { $Profile = "reemmor" }

$env:AWS_PROFILE = $Profile
$env:AWS_DEFAULT_REGION = $Region

Write-Host "`n=== PITER AWS SMS enablement ===" -ForegroundColor Cyan
Write-Host "Phone: $Phone  Profile: $Profile  Region: $Region`n"

function Test-SmsReady {
    & $Python (Join-Path $Root "scripts\diagnose_sms.py") 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

if (-not (Test-SmsReady)) {
    Write-Host "SMS service not enabled yet. Opening AWS Console tabs..." -ForegroundColor Yellow
    Write-Host "In the browser (logged in as account 329597159579):"
    Write-Host "  1. Complete any account verification prompts if shown"
    Write-Host "  2. End User Messaging: accept SMS terms"
    Write-Host "  3. Set monthly spend limit (e.g. `$$MonthlyLimit)"
    Write-Host "  4. Leave this window open — we'll poll every 15s`n"

    Start-Process "https://us-east-1.console.aws.amazon.com/sms-voice/home?region=us-east-1#/overview"
    Start-Process "https://console.aws.amazon.com/sns/v3/home?region=us-east-1#/mobile/text-messaging"
    Start-Process "https://portal.aws.amazon.com/billing/signup?type=resubscribe#/resubscribed"

    $deadline = (Get-Date).AddMinutes(20)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 15
        if (Test-SmsReady) {
            Write-Host "`nSMS service is enabled." -ForegroundColor Green
            break
        }
        Write-Host ("[{0}] Waiting for console opt-in..." -f (Get-Date).ToString("HH:mm:ss"))
    }

    if (-not (Test-SmsReady)) {
        Write-Host "`nTimed out. Finish console steps manually, then re-run:" -ForegroundColor Red
        Write-Host "  .\scripts\enable_sms.ps1`n"
        exit 1
    }
}

Write-Host "Setting SMS attributes (spend limit, transactional)..." -ForegroundColor Cyan
aws sns set-sms-attributes --attributes "MonthlySpendLimit=$MonthlyLimit,DefaultSMSType=Transactional,DeliveryStatusSuccessSamplingRate=100" --region $Region --profile $Profile
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: set-sms-attributes failed — set spend limit in console." -ForegroundColor Yellow
}

Write-Host "Adding sandbox destination $Phone (OTP will be sent)..." -ForegroundColor Cyan
$create = aws sns create-sms-sandbox-phone-number --phone-number $Phone --language-code en-US --region $Region --profile $Profile 2>&1
if ($LASTEXITCODE -ne 0) {
    if ($create -match "already exists|Verified") {
        Write-Host "Phone already in sandbox list."
    } else {
        Write-Host $create
    }
} else {
    Write-Host "OTP sent to $Phone"
    $otp = Read-Host "Enter the verification code from SMS"
    if ($otp) {
        aws sns verify-sms-sandbox-phone-number --phone-number $Phone --one-time-password $otp --region $Region --profile $Profile
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Verification failed. Re-run and enter the correct OTP." -ForegroundColor Red
            exit 1
        }
        Write-Host "Phone verified in SMS sandbox." -ForegroundColor Green
    }
}

Write-Host "`nRunning live notify test..." -ForegroundColor Cyan
& $Python (Join-Path $Root "scripts\test_live_notify.py")
exit $LASTEXITCODE
