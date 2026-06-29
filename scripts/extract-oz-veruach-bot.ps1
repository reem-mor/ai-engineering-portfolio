#Requires -Version 5.1
<#
.SYNOPSIS
  Export oz_veruach_bot/ to a standalone git repo directory.

.EXAMPLE
  .\scripts\extract-oz-veruach-bot.ps1 -OutputDir ..\oz-veruach-bot-export
  .\scripts\extract-oz-veruach-bot.ps1 -CleanCopy -OutputDir ..\oz-veruach-bot-export
#>
param(
    [string]$OutputDir = "..\oz-veruach-bot-export",
    [switch]$CleanCopy
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Prefix = "oz_veruach_bot"
$SplitBranch = "oz-veruach-bot-split"

Set-Location $RepoRoot

if ($CleanCopy) {
    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }
    $destPath = (Resolve-Path $OutputDir).Path
    robocopy (Join-Path $RepoRoot $Prefix) $destPath /E /XD .venv __pycache__ .pytest_cache .mypy_cache /NFL /NDL /NJH /NJS | Out-Null
    Copy-Item (Join-Path $RepoRoot "docs/extraction/oz-veruach-bot/README.stub.md") (Join-Path $destPath "README.md") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/oz-veruach-bot/AGENTS.stub.md") (Join-Path $destPath "AGENTS.md") -Force
    Write-Host "Clean copy ready at $destPath"
    exit 0
}

Write-Host "Creating subtree split branch '$SplitBranch'..."
git subtree split --prefix=$Prefix -b $SplitBranch

if (Test-Path $OutputDir) {
    Write-Warning "OutputDir exists: $OutputDir"
    exit 1
}

git clone . $OutputDir --branch $SplitBranch --single-branch

$inner = Join-Path (Resolve-Path $OutputDir).Path $Prefix
if (Test-Path $inner) {
    Get-ChildItem $inner -Force | ForEach-Object {
        Move-Item $_.FullName (Join-Path (Resolve-Path $OutputDir).Path $_.Name) -Force
    }
    Remove-Item $inner -Recurse -Force -ErrorAction SilentlyContinue
}

Copy-Item (Join-Path $RepoRoot "docs/extraction/oz-veruach-bot/README.stub.md") (Join-Path (Resolve-Path $OutputDir).Path "README.md") -Force
Copy-Item (Join-Path $RepoRoot "docs/extraction/oz-veruach-bot/AGENTS.stub.md") (Join-Path (Resolve-Path $OutputDir).Path "AGENTS.md") -Force

Write-Host @"

Next steps:
  cd $OutputDir
  git remote add origin https://github.com/reem-mor/oz-veruach-bot.git
  git push -u origin HEAD:main
"@
