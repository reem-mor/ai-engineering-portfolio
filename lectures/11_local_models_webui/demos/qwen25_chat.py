"""Qwen2.5-1.5B smoke test via llama-cpp-python.

See examples/io/qwen25_factual.json for recorded I/O.
"""

from __future__ import annotations

import argparse
import json
import sys

from _env import ensure_hf_token, n_gpu_layers

REPO_ID = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
FILENAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"


def main() -> int:
    parser = argparse.ArgumentParser(description="Qwen2.5 local chat smoke test")
    parser.add_argument(
        "--prompt",
        default="What is the capital of France?",
        help="User message",
    )
    parser.add_argument("--max-tokens", type=int, default=100)
    args = parser.parse_args()

    try:
        from llama_cpp import Llama
    except ImportError:
        print(
            "Install: pip install -r lectures/11_local_models_webui/requirements.txt "
            "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan",
            file=sys.stderr,
        )
        return 1

    ensure_hf_token()
    gpu = n_gpu_layers()

    llm = Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=FILENAME,
        n_ctx=2048,
        n_threads=8,
        n_gpu_layers=gpu,
        verbose=False,
    )

    messages = [{"role": "user", "content": args.prompt}]
    response = llm.create_chat_completion(messages=messages, max_tokens=args.max_tokens)
    msg = response["choices"][0]["message"]

    print("INPUT:", json.dumps(messages, ensure_ascii=False))
    print("OUTPUT:", json.dumps(msg, ensure_ascii=False, indent=2))
    print("usage:", response.get("usage"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
