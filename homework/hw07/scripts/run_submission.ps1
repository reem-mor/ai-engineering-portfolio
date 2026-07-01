# HW07 end-to-end submission workflow (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (Test-Path "..\..\.venv\Scripts\python.exe") {
    $py = "..\..\.venv\Scripts\python.exe"
} else {
    $py = "py"
}

function Invoke-Python {
    param([string[]]$Args)
    if ($py -eq "py") {
        & py -3.12 @Args
    } else {
        & $py @Args
    }
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $($Args -join ' ')" }
}

Write-Host "=== HW07 submission workflow ===" -ForegroundColor Cyan

Write-Host "`n[1/6] Verify environment..."
Invoke-Python @("scripts/verify_env.py")

Write-Host "`n[2/6] Unit tests (mock mode)..."
$env:HW07_MOCK_RAPIDAPI = "1"
Invoke-Python @("-m", "pytest", "tests/test_tools_server.py", "-q", "-m", "not live")

Write-Host "`n[3/6] Docker stack health..."
docker compose ps | Out-Host
$webui = Invoke-RestMethod -Uri "http://localhost:3000/health" -TimeoutSec 15
if (-not $webui.status) { throw "Open WebUI unhealthy" }
Write-Host "Open WebUI: OK"

Write-Host "`n[4/6] Tool server health (start in another terminal if missing)..."
try {
    $tools = Invoke-RestMethod -Uri "http://127.0.0.1:5005/health" -TimeoutSec 5
    Write-Host "Tool server: $($tools | ConvertTo-Json -Compress)"
} catch {
    Write-Warning "Tool server not reachable — run: .\scripts\start_tool_server.ps1 -MockRapidApi"
    throw
}

Write-Host "`n[5/6] Open WebUI setup (KB upload + index — may take 10-40 min)..."
Invoke-Python @("e2e/capture_screenshots.py", "--setup-only", "--skip-warmup")

Write-Host "`n[6/6] Screenshot capture (00-08)..."
Invoke-Python @("e2e/capture_screenshots.py", "--skip-warmup", "--kb-ready")

Write-Host "`n=== Submission workflow complete ===" -ForegroundColor Green
Get-ChildItem screenshots\*.png | Select-Object Name, Length | Format-Table
