# Start hw07 CVE tool server on host (required for Open WebUI OpenAPI tools)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$port = if ($env:TOOLS_SERVER_PORT) { $env:TOOLS_SERVER_PORT } else { "5005" }

if (Test-Path "..\.venv\Scripts\python.exe") {
    $py = "..\.venv\Scripts\python.exe"
} elseif (Test-Path "..\..\..\.venv\Scripts\python.exe") {
    $py = "..\..\..\.venv\Scripts\python.exe"
} else {
    $py = "py"
}

Write-Host "Starting tools_server on http://0.0.0.0:${port} ..."
if ($py -eq "py") {
    & py -3.12 -m uvicorn tools_server:app --host 0.0.0.0 --port $port --reload
} else {
    & $py -m uvicorn tools_server:app --host 0.0.0.0 --port $port --reload
}
