# Start hw07 Docker stack (Ollama + Open WebUI)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

docker compose pull open-webui
docker compose up -d
Write-Host "Waiting for containers..."
Start-Sleep -Seconds 15
docker compose ps

Write-Host "`nNext: docker exec hw07-ollama ollama pull nomic-embed-text"
Write-Host "       docker exec hw07-ollama ollama pull llama3.1"
Write-Host "Open WebUI: http://localhost:3000"
