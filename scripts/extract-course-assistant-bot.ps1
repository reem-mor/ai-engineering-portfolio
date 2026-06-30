#Requires -Version 5.1
<#
.SYNOPSIS
  Re-export course-assistant-bot from external repo (source tree no longer in archive).

.EXAMPLE
  .\scripts\extract-course-assistant-bot.ps1 -OutputDir C:\dev\course-assistant-bot
#>
param(
    [string]$OutputDir = "..\course-assistant-bot",
    [switch]$CleanCopy
)

$ErrorActionPreference = "Stop"
$ExternalRepo = "https://github.com/reem-mor/course-assistant-bot.git"

if ($CleanCopy -and (Test-Path $OutputDir)) {
    Remove-Item $OutputDir -Recurse -Force
}

if (-not (Test-Path $OutputDir)) {
    Write-Host "Cloning $ExternalRepo -> $OutputDir"
    git clone $ExternalRepo $OutputDir
} else {
    Write-Host "OutputDir already exists: $OutputDir (skipping clone)"
}

Write-Host "Done. Pointer in archive: flagships/course-assistant-bot/"
