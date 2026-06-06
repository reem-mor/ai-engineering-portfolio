# Run all verification from the PROJECT ROOT (not frontend/).
# Usage:  .\scripts\verify.ps1
#         .\scripts\verify.ps1 -AppUrl http://127.0.0.1:8080 -SkipLiveAws

param(
    [string]$AppUrl = "http://127.0.0.1:8080",
    [switch]$SkipLiveAws,
    [switch]$SkipE2e
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Error "Missing venv at $Python. From project root run: python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt"
}

Write-Host "==> pytest (offline)" -ForegroundColor Cyan
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> npm build (SPA)" -ForegroundColor Cyan
Push-Location (Join-Path $Root "frontend")
npm ci --silent 2>$null; if ($LASTEXITCODE -ne 0) { npm install }
npm run build
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

if (-not $SkipLiveAws) {
    Write-Host "==> KB smoke test (live Bedrock; requires AWS creds in .env)" -ForegroundColor Cyan
    & $Python scripts\kb_smoke_test.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "==> Skipped kb_smoke_test.py (-SkipLiveAws)" -ForegroundColor Yellow
}

if (-not $SkipE2e) {
    Write-Host "==> SPA E2E ($AppUrl)" -ForegroundColor Cyan
    $env:APP_URL = $AppUrl
    & $Python scripts\verify_e2e.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "==> Skipped verify_e2e.py (-SkipE2e)" -ForegroundColor Yellow
}

Write-Host "All requested checks passed." -ForegroundColor Green
