# Query /api/bootstrap notification readiness (PowerShell-safe)
param(
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$json = curl.exe -s "$BaseUrl/api/bootstrap"
if (-not $json) {
    Write-Error "No response from $BaseUrl — is the app running? Use .\scripts\run-local.ps1"
}

$data = $json | ConvertFrom-Json
$n = $data.notification
Write-Host "mode:              $($n.mode)"
Write-Host "live_dispatch:     $($n.live_dispatch_enabled)"
Write-Host "email_configured:  $($n.email_configured)"
Write-Host "sms_configured:    $($n.sms_configured)"
Write-Host "sms_delivery_ready:$($n.sms_delivery_ready)"
if ($n.sms_delivery_message) {
    Write-Host "sms_message:       $($n.sms_delivery_message)"
}
