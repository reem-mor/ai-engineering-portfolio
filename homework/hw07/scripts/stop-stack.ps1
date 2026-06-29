#Requires -Version 5.1
<#
.SYNOPSIS
  Stop HW07 stack: tool server background job + Open WebUI container.
#>
$ErrorActionPreference = "Stop"
$Hw07Root = Split-Path -Parent $PSScriptRoot

Write-Host "Stopping hw07-tool-server job..." -ForegroundColor Cyan
$job = Get-Job -Name "hw07-tool-server" -ErrorAction SilentlyContinue
if ($job) {
    Stop-Job -Job $job -Force
    Remove-Job -Job $job -Force
    Write-Host "Tool server job stopped." -ForegroundColor Green
} else {
    Write-Host "No hw07-tool-server job found." -ForegroundColor Yellow
}

Write-Host "Stopping Open WebUI container..." -ForegroundColor Cyan
Push-Location $Hw07Root
try {
    docker compose down
} finally {
    Pop-Location
}
Write-Host "HW07 stack stopped." -ForegroundColor Green
