"""Qwen3.6-27B multimodal smoke test via llama-cpp-python (vision profile, no MTP).

Requires:
  pip install -r lectures/11_local_models_webui/requirements.txt
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
  lectures/11_local_models_webui/scripts/download_qwen36.ps1

Env:
  HF_TOKEN          Hugging Face token (for gated downloads)
  QWEN36_REPO       Default unsloth/Qwen3.6-27B-MTP-GGUF
  QWEN36_QUANT      Glob for main GGUF (default *UD-Q4_K_XL*)
  QWEN36_MMPROJ     Vision projector file (default mmproj-F16.gguf)
  QWEN36_N_CTX      Context size (default 8192)
  QWEN36_N_GPU_LAYERS  GPU layers; lower if Arc 140V TDR/crashes (default 35)
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")

REPO_ID = os.getenv("QWEN36_REPO", "unsloth/Qwen3.6-27B-MTP-GGUF")
QUANT_PATTERN = os.getenv("QWEN36_QUANT", "*UD-Q4_K_XL*")
MMPROJ_FILE = os.getenv("QWEN36_MMPROJ", "mmproj-F16.gguf")
N_CTX = int(os.getenv("QWEN36_N_CTX", "8192"))
N_GPU_LAYERS = int(os.getenv("QWEN36_N_GPU_LAYERS", "35"))

IMAGE_URL = (
    "https://cdn.britannica.com/61/93061-050-99147DCE/"
    "Statue-of-Liberty-Island-New-York-Bay.jpg"
)


def main() -> int:
    try:
        from llama_cpp import Llama
        from llama_cpp.llama_chat_format import MTMDChatHandler
    except ImportError:
        print(
            "llama-cpp-python not installed. Run:\n"
            "  pip install -r lectures/11_local_models_webui/requirements.txt "
            "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu",
            file=sys.stderr,
        )
        return 1

    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if hf_token:
        os.environ.setdefault("HF_TOKEN", hf_token)

    print(f"Loading mmproj {MMPROJ_FILE} from {REPO_ID} ...")
    t0 = time.perf_counter()
    chat_handler = MTMDChatHandler.from_pretrained(
        repo_id=REPO_ID,
        filename=MMPROJ_FILE,
    )

    print(f"Loading model {QUANT_PATTERN} (n_ctx={N_CTX}, n_gpu_layers={N_GPU_LAYERS}) ...")
    llm = Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=QUANT_PATTERN,
        chat_handler=chat_handler,
        n_ctx=N_CTX,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False,
    )
    load_s = time.perf_counter() - t0
    print(f"Model loaded in {load_s:.1f}s")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in one sentence."},
                {"type": "image_url", "image_url": {"url": IMAGE_URL}},
            ],
        }
    ]

    print("Generating ...")
    t1 = time.perf_counter()
    response = llm.create_chat_completion(messages=messages, max_tokens=128)
    gen_s = time.perf_counter() - t1

    text = response["choices"][0]["message"]["content"]
    usage = response.get("usage", {})
    print("\n--- Response ---")
    print(text)
    print("\n--- Stats ---")
    print(f"load_s={load_s:.1f} gen_s={gen_s:.1f} usage={usage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
