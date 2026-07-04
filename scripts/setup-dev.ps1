#Requires -Version 5.1
<#
.SYNOPSIS
  Bootstrap root venv, dev tools, lecture-08 MCP deps, and .env from example.
.EXAMPLE
  .\scripts\setup-dev.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Python venv (.venv)"
if (-not (Test-Path .venv)) {
    python -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements-dev.txt

Write-Host "==> Lecture 08 MCP server deps"
$Lec08 = Join-Path $Root "lectures\08_mcp"
if (-not (Test-Path (Join-Path $Lec08 ".venv"))) {
    python -m venv (Join-Path $Lec08 ".venv")
}
& (Join-Path $Lec08 ".venv\Scripts\pip.exe") install -r (Join-Path $Lec08 "requirements.txt")

Write-Host "==> Playwright MCP + Chromium (browser automation / hw07 E2E)"
if (Get-Command npx -ErrorAction SilentlyContinue) {
    npx -y @playwright/mcp@latest --help | Out-Null
    npx -y playwright install chromium
} else {
    Write-Warning "Node.js/npx not found — install Node 18+ for Playwright MCP (.mcp.json)."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — fill in your keys locally."
} else {
    Write-Host ".env already exists — skipped."
}

Write-Host @"

Done. Next:
  .\.venv\Scripts\Activate.ps1
  ruff check .
  See docs/AGENT-TOOLING.md for MCP setup (.mcp.json at repo root).
  Optional: .\scripts\clean-workspace.ps1  (remove local caches / old flagship copies)
  Layout: docs/STRUCTURE.md
"@
