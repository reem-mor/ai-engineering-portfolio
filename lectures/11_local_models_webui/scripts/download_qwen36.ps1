#Requires -Version 5.1
<#
.SYNOPSIS
  Download Qwen3.6-27B-MTP-GGUF quant + mmproj from Hugging Face (idempotent).
.EXAMPLE
  .\lectures\11_local_models_webui\scripts\download_qwen36.ps1
  .\lectures\11_local_models_webui\scripts\download_qwen36.ps1 -QuantPattern "*UD-Q3_K_XL*"
#>
param(
    [string]$RepoId = $env:QWEN36_REPO,
    [string]$QuantPattern = "*UD-Q4_K_XL*"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Root .venv not found. Run scripts/setup-dev.ps1 first."
}

if ($RepoId) { $env:QWEN36_REPO = $RepoId }
if ($QuantPattern) { $env:QWEN36_QUANT = $QuantPattern }

& $Python (Join-Path $PSScriptRoot "download_qwen36.py")
if ($LASTEXITCODE -ne 0) {
    throw "download_qwen36.py failed (exit $LASTEXITCODE)"
}
