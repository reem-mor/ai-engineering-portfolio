#!/usr/bin/env pwsh
# Run from Cursor / PowerShell — uses USERPROFILE only (handles names with apostrophes).

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $Root

$VenvPy = Join-Path $env:USERPROFILE "amdocs-ai-course\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $VenvPy)) {
    Write-Error "Venv Python not found: $VenvPy"
    exit 1
}

& $VenvPy -m pip install -r (Join-Path $Root "requirements.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Starting API at http://127.0.0.1:8000 (health: /api/health)" -ForegroundColor Green
& $VenvPy -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
