#Requires -Version 5.1
param(
    [string]$OutputDir = "..\piter-aiops",
    [switch]$CleanCopy
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Prefix = "projects/piter-aiops"
$SplitBranch = "piter-aiops-split"
$ExcludeDirs = @(".venv", "node_modules", "frontend/node_modules", "dist", "build", "__pycache__", ".pytest_cache", "incoming")

Set-Location $RepoRoot

function Copy-PiterTree {
    param([string]$Dest)
    if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest | Out-Null }
    robocopy (Join-Path $RepoRoot $Prefix) $Dest /E /XD $ExcludeDirs /XF .env *.tar EXTRACTION.md /NFL /NDL /NJH /NJS | Out-Null
}

function Add-PortfolioFiles {
    param([string]$Dest)
    Copy-Item (Join-Path $RepoRoot "LICENSE") (Join-Path $Dest "LICENSE") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/piter-aiops/AGENTS.md") (Join-Path $Dest "AGENTS.md") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/piter-aiops/CLAUDE.md") (Join-Path $Dest "CLAUDE.md") -Force
    $banner = @"
> **Portfolio flagship** — agentic incident response on AWS Bedrock. Course archive: [amdocs-ai-course](https://github.com/reem-mor/amdocs-ai-course).

"@
    $readme = Join-Path $Dest "README.md"
    if (Test-Path $readme) {
        $content = Get-Content $readme -Raw -Encoding UTF8
        if ($content -notmatch "Portfolio flagship") {
            Set-Content $readme ($banner + $content) -Encoding UTF8 -NoNewline
        }
    }
}

if ($CleanCopy) {
    if (Test-Path $OutputDir) { Remove-Item $OutputDir -Recurse -Force }
    Copy-PiterTree -Dest $OutputDir
    Add-PortfolioFiles -Dest (Resolve-Path $OutputDir).Path
    Write-Host "Clean copy -> $OutputDir"
    exit 0
}

Write-Host "Creating subtree split branch '$SplitBranch'..."
git subtree split --prefix=$Prefix -b $SplitBranch
if (Test-Path $OutputDir) { throw "OutputDir exists: $OutputDir" }
git clone . $OutputDir --branch $SplitBranch --single-branch
$inner = Join-Path (Resolve-Path $OutputDir).Path "projects/piter-aiops"
if (Test-Path $inner) {
    Get-ChildItem $inner -Force | ForEach-Object {
        Move-Item $_.FullName (Join-Path (Resolve-Path $OutputDir).Path $_.Name) -Force
    }
    Remove-Item (Split-Path $inner -Parent) -Recurse -Force -ErrorAction SilentlyContinue
}
Remove-Item (Join-Path $OutputDir "EXTRACTION.md") -Force -ErrorAction SilentlyContinue
Add-PortfolioFiles -Dest (Resolve-Path $OutputDir).Path
Write-Host "Export ready at $OutputDir"
