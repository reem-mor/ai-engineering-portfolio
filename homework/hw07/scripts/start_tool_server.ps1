# Start hw07 tool server (host) — required for Open WebUI tools
param(
    [switch]$MockRapidApi
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if ($MockRapidApi) {
    $env:HW07_MOCK_RAPIDAPI = "1"
}

if (Test-Path "..\.venv\Scripts\python.exe") {
    $py = "..\.venv\Scripts\python.exe"
} else {
    $py = "py"
    $pyArgs = @("-3.12")
}

Write-Host "Starting tools_server on http://0.0.0.0:5005 ..."
if ($py -eq "py") {
    & py -3.12 -m uvicorn tools_server:app --host 0.0.0.0 --port 5005
} else {
    & $py -m uvicorn tools_server:app --host 0.0.0.0 --port 5005
}
