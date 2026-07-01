"""Shared env helpers for lecture 11 demos."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
LECTURE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_IO = LECTURE_ROOT / "examples" / "io"

load_dotenv(REPO_ROOT / ".env")


def hf_token() -> str | None:
    return os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN") or None


def ensure_hf_token() -> None:
    token = hf_token()
    if token:
        os.environ.setdefault("HF_TOKEN", token)


def n_gpu_layers(default: int = 999) -> int:
    """Intel Arc / Vulkan: use GPU offload; CPU-only repack may crash on some hosts."""
    return int(os.getenv("QWEN_N_GPU_LAYERS", os.getenv("QWEN36_N_GPU_LAYERS", str(default))))


def llama_server_base_url() -> str:
    port = os.getenv("LLAMA_SERVER_PORT", "8080")
    return os.getenv("LLAMA_SERVER_BASE_URL", f"http://127.0.0.1:{port}/v1")
