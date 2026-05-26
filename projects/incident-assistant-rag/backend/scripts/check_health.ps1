#!/usr/bin/env pwsh
# Call after dev_local.ps1 (or uvicorn). GET /api/health

try {
    $r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -Method Get -TimeoutSec 10
    $r | ConvertTo-Json -Depth 8
    Write-Host "OK: localhost responded." -ForegroundColor Green
    exit 0
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
