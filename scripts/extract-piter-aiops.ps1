#Requires -Version 5.1
<#
.SYNOPSIS
  Clone piter-aiops from its external repository (source tree no longer in archive).

.EXAMPLE
  .\scripts\extract-piter-aiops.ps1 -OutputDir C:\dev\piter-aiops
#>
param(
    [string]$OutputDir = "..\piter-aiops",
    [switch]$CleanCopy
)

$ErrorActionPreference = "Stop"
$ExternalRepo = "https://github.com/reem-mor/piter-aiops.git"

if ($CleanCopy -and (Test-Path $OutputDir)) {
    Remove-Item $OutputDir -Recurse -Force
}

if (-not (Test-Path $OutputDir)) {
    Write-Host "Cloning $ExternalRepo -> $OutputDir"
    git clone $ExternalRepo $OutputDir
} else {
    Write-Host "OutputDir already exists: $OutputDir (skipping clone)"
}

Write-Host "Done. Pointer in archive: flagships/piter-aiops/"
