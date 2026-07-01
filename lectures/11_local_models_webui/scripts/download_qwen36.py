"""Download Qwen3.6-27B-MTP-GGUF quant + mmproj from Hugging Face (idempotent)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import snapshot_download

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")

REPO_ID = os.getenv("QWEN36_REPO", "unsloth/Qwen3.6-27B-MTP-GGUF")
QUANT_PATTERN = os.getenv("QWEN36_QUANT", "*UD-Q4_K_XL*")
MMPROJ_FILE = os.getenv("QWEN36_MMPROJ", "mmproj-F16.gguf")


def main() -> int:
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not token:
        print("Warning: HF_TOKEN not set — gated files may fail.", file=sys.stderr)

    print(f"==> Downloading {REPO_ID}")
    print(f"    mmproj: {MMPROJ_FILE}")
    path = snapshot_download(
        repo_id=REPO_ID,
        allow_patterns=[QUANT_PATTERN, MMPROJ_FILE],
        token=token or None,
    )
    print(f"Done. Cache path: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
