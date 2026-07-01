---
name: local-models
description: Use when running local LLMs — Qwen3.6 via llama-cpp-python, llama-server OpenAI API, Ollama/Open WebUI hw07 stack, Hugging Face model download, or Intel Arc Vulkan tuning.
---

# Local Models — Qwen3.6 + Ollama + Open WebUI

## When to use

- Installing or running `unsloth/Qwen3.6-27B-MTP-GGUF`
- Intel Arc / Lunar Lake (shared VRAM) tuning
- Wiring Open WebUI to host `llama-server` on port 8080
- Lecture 11 demos under `lectures/11_local_models_webui/`

## Read first

1. [`lectures/11_local_models_webui/README.md`](../../lectures/11_local_models_webui/README.md)
2. [`homework/hw07/README.md`](../../homework/hw07/README.md) — Open WebUI + Ollama KB/tools
3. Unsloth MTP guide: https://unsloth.ai/docs/models/mtp

## Stack roles

| Layer | Port | Role |
|-------|------|------|
| Ollama (Docker) | internal 11434 | `llama3.2:3b` chat, `nomic-embed-text` KB embeddings |
| llama-server (host) | 8080 | Qwen3.6 text or vision via OpenAI-compatible API |
| Open WebUI | 3000 | Browser UI; connects to both Ollama and llama-server |
| hw07 tool server | 5005 | Live JSearch jobs (`host.docker.internal:5005`) |

## Quick start (Windows)

```powershell
# From repo root — deps already in .venv after install
.\lectures\11_local_models_webui\scripts\download_qwen36.ps1
.\lectures\11_local_models_webui\scripts\start_llama_server.ps1          # text
.\lectures\11_local_models_webui\scripts\start_llama_server.ps1 -Profile vision

# Vision smoke test
python lectures/11_local_models_webui/demos/qwen36_vision_chat.py

# hw07 stack (separate terminal)
cd homework\hw07
docker compose up -d
docker exec hw07-ollama ollama pull llama3.2:3b
docker exec hw07-ollama ollama pull nomic-embed-text
```

## Env (repo-root `.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `HF_TOKEN` | — | HF download + Hugging Face Cursor plugin MCP |
| `QWEN36_REPO` | `unsloth/Qwen3.6-27B-MTP-GGUF` | Model repo |
| `QWEN36_QUANT` | `*UD-Q4_K_XL*` | ~17 GB quant (not BF16) |
| `QWEN36_MMPROJ` | `mmproj-F16.gguf` | Vision projector (do not use `*mmproj*` glob) |
| `QWEN36_N_CTX` | `8192` | Context; lower if OOM |
| `QWEN36_N_GPU_LAYERS` | `35` | Partial offload on Arc 140V TDR |
| `LLAMA_SERVER_PORT` | `8080` | OpenAI API for Open WebUI |

## Two profiles (do not mix)

| Profile | MTP speed | Vision / mmproj |
|---------|-----------|-----------------|
| **text** (`start_llama_server.ps1`) | Use llama.cpp binary for full MTP | No |
| **vision** (`-Profile vision` or `qwen36_vision_chat.py`) | No | Yes — needs `MTMDChatHandler` + mmproj |

Unsloth: `--mmproj` is not yet supported with MTP.

## Open WebUI admin

1. **Connections → Ollama:** default (`http://ollama:11434`)
2. **Connections → OpenAI API:** `http://host.docker.internal:8080/v1` (no key)
3. **Documents → Embeddings:** `nomic-embed-text`

## MCP (Cursor)

- **Hugging Face:** Cursor plugin (not in `.mcp.json`); needs `HF_TOKEN`
- **kaggle, playwright:** root [`.mcp.json`](../../.mcp.json)
- Do **not** add Ollama MCP — use Docker CLI / Open WebUI

## Intel Arc 140V mitigations

- Use `UD-Q4_K_XL` or `UD-Q3_K_XL`, not BF16
- Lower `QWEN36_N_GPU_LAYERS` if TDR freezes
- CPU wheel (default): `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`
- Vulkan wheel (optional GPU): `.../whl/vulkan` — may TDR on Arc 140V with 27B

## Guardrails

- Never commit `.env` or model weights
- hw07 CI stays offline — no llama-cpp in GitHub Actions
- Qwen3.6 vision does not work reliably in Ollama (separate mmproj)
