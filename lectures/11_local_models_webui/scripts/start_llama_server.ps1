#Requires -Version 5.1
<#
.SYNOPSIS
  Start llama-cpp-python OpenAI-compatible server for Qwen3.6 on port 8080.
.PARAMETER Profile
  text  — UD-Q4_K_XL, text-only (default; fastest for chat/coding)
  vision — UD-Q4_K_XL + mmproj via MTMD (no MTP; use for images)
.EXAMPLE
  .\lectures\11_local_models_webui\scripts\start_llama_server.ps1
  .\lectures\11_local_models_webui\scripts\start_llama_server.ps1 -Profile vision
#>
param(
    [ValidateSet("text", "vision")]
    [string]$Profile = "text",
    [int]$Port = 0,
    [int]$NGpuLayers = 0,
    [int]$Ctx = 0
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Root .venv not found. Run scripts/setup-dev.ps1 first."
}

# Load repo .env
$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"').Trim("'")
            if ($name -and $value -and -not [string]::IsNullOrWhiteSpace($value) -and $value -notmatch '^your_.*_here$') {
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
}

$RepoId = if ($env:QWEN36_REPO) { $env:QWEN36_REPO } else { "unsloth/Qwen3.6-27B-MTP-GGUF" }
$Quant = if ($env:QWEN36_QUANT) { $env:QWEN36_QUANT } else { "*UD-Q4_K_XL*" }
$Mmproj = if ($env:QWEN36_MMPROJ) { $env:QWEN36_MMPROJ } else { "mmproj-F16.gguf" }
if (-not $Port) { $Port = if ($env:LLAMA_SERVER_PORT) { [int]$env:LLAMA_SERVER_PORT } else { 8080 } }
if (-not $Ctx) { $Ctx = if ($env:QWEN36_N_CTX) { [int]$env:QWEN36_N_CTX } else { 8192 } }
if (-not $NGpuLayers) {
    $NGpuLayers = if ($env:QWEN36_N_GPU_LAYERS) { [int]$env:QWEN36_N_GPU_LAYERS } else { 35 }
}

$ServerArgs = @(
    "-m", "llama_cpp.server",
    "--host", "0.0.0.0",
    "--port", "$Port",
    "--hf_model_repo_id", $RepoId,
    "--model", $Quant,
    "--n_gpu_layers", "$NGpuLayers",
    "--n_ctx", "$Ctx"
)

if ($Profile -eq "vision") {
    Write-Host "Starting vision profile (MTMD + mmproj, no MTP) on http://127.0.0.1:$Port/v1"
    $ServerArgs += @("--chat_format", "mtmd", "--clip_model_path", "hf://$RepoId/$Mmproj")
} else {
    Write-Host "Starting text profile on http://127.0.0.1:$Port/v1"
    Write-Host "Note: MTP speculative decoding is not exposed by llama_cpp.server; use llama.cpp binary for MTP."
    $ServerArgs += @("--chat_format", "chatml")
}

Write-Host "Repo: $RepoId  Quant: $Quant  n_ctx=$Ctx  n_gpu_layers=$NGpuLayers"
Write-Host "Health: curl.exe http://127.0.0.1:$Port/v1/models"
Write-Host ""

& $Python @ServerArgs
