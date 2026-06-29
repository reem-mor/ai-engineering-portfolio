#Requires -Version 5.1
<#
.SYNOPSIS
  Export projects/piter-aiops to a standalone git repo directory.

.DESCRIPTION
  Option 1 (default): git subtree split + clone to OutputDir.
  Option 2 (-CleanCopy): robocopy source without history (faster smoke test).

  After export, copy docs/extraction/piter-aiops/*.stub.md to README.md / AGENTS.md
  in the new repo root and rename .stub.md extensions.

.EXAMPLE
  .\scripts\extract-piter-aiops.ps1 -OutputDir ..\piter-aiops-export
#>
param(
    [string]$OutputDir = "..\piter-aiops-export",
    [switch]$CleanCopy
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Prefix = "projects/piter-aiops"
$SplitBranch = "piter-aiops-split"

Set-Location $RepoRoot

if ($CleanCopy) {
    $dest = Resolve-Path -LiteralPath $OutputDir -ErrorAction SilentlyContinue
    if (-not $dest) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }
    $destPath = (Resolve-Path $OutputDir).Path
    Write-Host "Clean copy -> $destPath"
    robocopy (Join-Path $RepoRoot $Prefix) $destPath /E /XD .venv node_modules frontend/node_modules dist build __pycache__ .pytest_cache /NFL /NDL /NJH /NJS | Out-Null
    Copy-Item (Join-Path $RepoRoot "docs/extraction/piter-aiops/README.stub.md") (Join-Path $destPath "README.md") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/piter-aiops/AGENTS.stub.md") (Join-Path $destPath "AGENTS.md") -Force
    Write-Host "Done. cd $destPath && git init && git add . && git commit -m 'chore: initial import from course archive'"
    exit 0
}

Write-Host "Creating subtree split branch '$SplitBranch' (may take a minute)..."
git subtree split --prefix=$Prefix -b $SplitBranch

if (Test-Path $OutputDir) {
    Write-Warning "OutputDir exists: $OutputDir — remove or choose another path."
    exit 1
}

git clone . $OutputDir --branch $SplitBranch --single-branch
Write-Host "Cloned to $OutputDir"

$inner = Join-Path (Resolve-Path $OutputDir).Path "projects/piter-aiops"
if (Test-Path $inner) {
    Write-Host "Flattening projects/piter-aiops/ to repo root..."
    Get-ChildItem $inner -Force | ForEach-Object {
        Move-Item $_.FullName (Join-Path (Resolve-Path $OutputDir).Path $_.Name) -Force
    }
    Remove-Item (Split-Path $inner -Parent) -Recurse -Force -ErrorAction SilentlyContinue
}

Copy-Item (Join-Path $RepoRoot "docs/extraction/piter-aiops/README.stub.md") (Join-Path (Resolve-Path $OutputDir).Path "README.md") -Force
Copy-Item (Join-Path $RepoRoot "docs/extraction/piter-aiops/AGENTS.stub.md") (Join-Path (Resolve-Path $OutputDir).Path "AGENTS.md") -Force

Write-Host @"

Next steps:
  cd $OutputDir
  git remote add origin https://github.com/reem-mor/piter-aiops.git
  git push -u origin HEAD:main

Then update the archive pointer — see projects/piter-aiops/EXTRACTION.md
"@
