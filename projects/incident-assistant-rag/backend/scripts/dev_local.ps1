#!/usr/bin/env pwsh
# Run from Cursor / PowerShell — prefers repo-root .venv, then falls back to python on PATH.

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $Root

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")
$VenvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPy)) {
    $VenvPy = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $VenvPy) {
    Write-Error "Python not found. Create repo venv: python -m venv .venv (from $RepoRoot)"
    exit 1
}

& $VenvPy -m pip install -r (Join-Path $Root "requirements.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Starting API at http://127.0.0.1:8000 (health: /api/health)" -ForegroundColor Green
& $VenvPy -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
