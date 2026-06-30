#Requires -Version 5.1
<#
.SYNOPSIS
  Remove local-only clutter from the workspace (gitignored artifacts).

.DESCRIPTION
  Safe to run anytime. Does NOT touch committed course code, homework, or projects.
  Removes extracted-flagship copies, caches, and root-level experiment data.

.EXAMPLE
  .\scripts\clean-workspace.ps1
  .\scripts\clean-workspace.ps1 -WhatIf
#>
param([switch]$WhatIf)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Targets = @(
    "projects/piter-aiops",
    "data",
    "catboost_info",
    ".agents",
    ".pytest_cache",
    ".ruff_cache",
    ".firecrawl",
    ".playwright-mcp",
    "docs/superpowers",
    "docs/extraction/oz-veruach-bot"
)

foreach ($rel in $Targets) {
    $path = Join-Path $RepoRoot $rel
    if (-not (Test-Path $path)) { continue }
    if ($WhatIf) {
        Write-Host "[WhatIf] Would remove: $rel"
    } else {
        Write-Host "Removing: $rel"
        Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Done. Clone flagships separately: see flagships/README.md"
