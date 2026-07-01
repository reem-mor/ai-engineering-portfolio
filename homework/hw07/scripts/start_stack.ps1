# Start hw07 Docker stack (Ollama + Open WebUI)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

docker compose pull open-webui
docker compose up -d
Write-Host "Waiting for healthchecks..."
Start-Sleep -Seconds 15
$ps = docker compose ps --format json | ConvertFrom-Json
$webui = $ps | Where-Object { $_.Service -eq 'open-webui' }
if ($webui.Health -ne 'healthy') {
    Write-Warning "Open WebUI not healthy — if upgrading from 0.6.x, run: python scripts\fix_webui_db_migration.py (see README)"
    docker compose logs open-webui --tail 20
}
docker compose ps

$healthy = docker compose ps --format json | ConvertFrom-Json
foreach ($c in $healthy) {
    if ($c.Health -and $c.Health -ne "healthy") {
        Write-Warning "$($c.Name) is $($c.Health) — check: docker compose logs $($c.Service)"
    }
}

Write-Host "`nNext: docker exec hw07-ollama ollama pull llama3.2:3b"
Write-Host "       docker exec hw07-ollama ollama pull nomic-embed-text"
Write-Host "Open WebUI: http://localhost:3000"
