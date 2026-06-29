#Requires -Version 5.1
<#
.SYNOPSIS
  Export oz_veruach_bot/ to standalone repo (default: course-assistant-bot).

.EXAMPLE
  .\scripts\extract-course-assistant-bot.ps1 -CleanCopy -OutputDir C:\dev\course-assistant-bot
#>
param(
    [string]$OutputDir = "..\course-assistant-bot",
    [switch]$CleanCopy
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Prefix = "oz_veruach_bot"
$SplitBranch = "course-assistant-bot-split"
$ExcludeDirs = @(".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")

Set-Location $RepoRoot

function Copy-BotTree {
    param([string]$Dest)
    if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest | Out-Null }
    robocopy (Join-Path $RepoRoot $Prefix) $Dest /E /XD $ExcludeDirs /XF .env EXTRACTION.md /NFL /NDL /NJH /NJS | Out-Null
}

function Add-PortfolioFiles {
    param([string]$Dest)
    Copy-Item (Join-Path $RepoRoot "LICENSE") (Join-Path $Dest "LICENSE") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/course-assistant-bot/AGENTS.md") (Join-Path $Dest "AGENTS.md") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/course-assistant-bot/CLAUDE.md") (Join-Path $Dest "CLAUDE.md") -Force
    Copy-Item (Join-Path $RepoRoot "docs/extraction/course-assistant-bot/.github") (Join-Path $Dest ".github") -Recurse -Force
    $banner = @"
> **Portfolio project** — bilingual Telegram course ops bot. Extracted from [amdocs-ai-course](https://github.com/reem-mor/amdocs-ai-course).

"@
    $readme = Join-Path $Dest "README.md"
    if (Test-Path $readme) {
        $content = Get-Content $readme -Raw -Encoding UTF8
        if ($content -notmatch "Portfolio project") {
            Set-Content $readme ($banner + $content) -Encoding UTF8 -NoNewline
        }
    }
}

if ($CleanCopy) {
    if (Test-Path $OutputDir) { Remove-Item $OutputDir -Recurse -Force }
    Copy-BotTree -Dest $OutputDir
    Add-PortfolioFiles -Dest (Resolve-Path $OutputDir).Path
    Write-Host "Clean copy -> $OutputDir"
    exit 0
}

Write-Host "Creating subtree split branch '$SplitBranch'..."
git subtree split --prefix=$Prefix -b $SplitBranch
if (Test-Path $OutputDir) { throw "OutputDir exists: $OutputDir" }
git clone . $OutputDir --branch $SplitBranch --single-branch
$inner = Join-Path (Resolve-Path $OutputDir).Path $Prefix
if (Test-Path $inner) {
    Get-ChildItem $inner -Force | ForEach-Object {
        Move-Item $_.FullName (Join-Path (Resolve-Path $OutputDir).Path $_.Name) -Force
    }
    Remove-Item $inner -Recurse -Force -ErrorAction SilentlyContinue
}
Remove-Item (Join-Path $OutputDir "EXTRACTION.md") -Force -ErrorAction SilentlyContinue
Add-PortfolioFiles -Dest (Resolve-Path $OutputDir).Path
Write-Host "Export ready at $OutputDir"
