#Requires -Version 5.1
<#
.SYNOPSIS
  Start HW07 stack: Open WebUI (Docker) + tool server (host uvicorn).

.DESCRIPTION
  Preflight checks for docker, ollama, and ports 3001/5005, then brings up
  docker compose and the FastAPI tool server in a background job.
#>
param(
    [switch]$MockRapidApi,
    [int]$TimeoutSec = 120
)

$ErrorActionPreference = "Stop"
$Hw07Root = Split-Path -Parent $PSScriptRoot
$ToolsDir = Join-Path $Hw07Root "open-webui-tools"
$RepoVenvPython = Join-Path (Split-Path -Parent (Split-Path -Parent $Hw07Root)) ".venv\Scripts\python.exe"
$Python = if (Test-Path $RepoVenvPython) { $RepoVenvPython } else { "python" }

function Test-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Test-PortFree([int]$Port) {
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($conn) {
        throw "Port $Port is already in use. Stop the conflicting process or run stop-stack.ps1."
    }
}

function Wait-HttpOk([string]$Url, [int]$TimeoutSeconds) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    return $false
}

Write-Host "=== HW07 stack preflight ===" -ForegroundColor Cyan
Test-Command docker
Test-Command ollama

$ollamaList = ollama list 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Ollama is not running or not installed. Start Ollama and run: ollama pull llama3.1"
}
if ($ollamaList -notmatch "(?i)llama|qwen|gpt-oss") {
    Write-Warning "No chat model found in ollama list. Recommended: ollama pull llama3.2:3b"
}

# Only check ports if services are not already our stack
$port3001 = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
$port5005 = Get-NetTCPConnection -LocalPort 5005 -ErrorAction SilentlyContinue
if (-not $port3001) { Test-PortFree 3001 }
if (-not $port5005) { Test-PortFree 5005 }

Write-Host "Starting Open WebUI via docker compose..." -ForegroundColor Cyan
Push-Location $Hw07Root
try {
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }
} finally {
    Pop-Location
}

if (-not (Wait-HttpOk "http://localhost:3001" $TimeoutSec)) {
    throw "Open WebUI did not become ready at http://localhost:3001 within ${TimeoutSec}s"
}
Write-Host "Open WebUI ready: http://localhost:3001" -ForegroundColor Green

# Tool server env
$envFile = Join-Path $ToolsDir ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $ToolsDir ".env.example") $envFile
    Write-Warning "Created $envFile from .env.example - set RAPIDAPI_KEY for live API calls."
}
if ($MockRapidApi) {
    $env:HW07_MOCK_RAPIDAPI = "1"
    Write-Host "HW07_MOCK_RAPIDAPI=1 (deterministic tool responses)" -ForegroundColor Yellow
}

# Stop prior tool-server job if present
$existing = Get-Job -Name "hw07-tool-server" -ErrorAction SilentlyContinue
if ($existing) {
    Stop-Job -Job $existing -Force
    Remove-Job -Job $existing -Force
}

Write-Host "Starting tool server on :5005..." -ForegroundColor Cyan
$job = Start-Job -Name "hw07-tool-server" -ScriptBlock {
    param($ToolsDirPath, $PythonPath, $MockMode)
    Set-Location $ToolsDirPath
    if ($MockMode) { $env:HW07_MOCK_RAPIDAPI = "1" }
    & $PythonPath -m uvicorn tools_server:app --host 0.0.0.0 --port 5005
} -ArgumentList $ToolsDir, $Python, ([bool]$MockRapidApi)

Start-Sleep -Seconds 2
if (-not (Wait-HttpOk "http://localhost:5005/health" 60)) {
    Receive-Job -Job $job
    throw "Tool server did not become ready at http://localhost:5005/health"
}

$health = Invoke-RestMethod -Uri "http://localhost:5005/health"
Write-Host "Tool server ready: http://localhost:5005" -ForegroundColor Green
Write-Host ("  status={0} rapidapi_configured={1} mock_mode={2}" -f $health.status, $health.rapidapi_configured, $health.mock_mode)

Write-Host ""
Write-Host "=== Stack running ===" -ForegroundColor Green
Write-Host "  Open WebUI:    http://localhost:3001"
Write-Host "  Tool server:   http://localhost:5005/docs"
Write-Host "  Tool URL (Docker): http://host.docker.internal:5005"
Write-Host ""
Write-Host 'Run Playwright: cd homework/hw07/e2e; npm install; npx playwright test'
Write-Host 'Stop stack:     homework/hw07/scripts/stop-stack.ps1'
