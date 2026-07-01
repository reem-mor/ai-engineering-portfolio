"""Qwen3 hybrid thinking demo — fast (/no_think) vs reasoning modes.

See examples/io/qwen3_*.json for recorded I/O.
"""

from __future__ import annotations

import argparse
import json
import sys

from _env import ensure_hf_token, n_gpu_layers

REPO_ID = "Qwen/Qwen3-1.7B-GGUF"
FILENAME = "Qwen3-1.7B-Q8_0.gguf"
THINK_OPEN = chr(60) + "think" + chr(62)
THINK_CLOSE = chr(60) + "/think" + chr(62)


def split_thinking(raw: str) -> dict[str, str | None]:
    if THINK_CLOSE in raw:
        pre, post = raw.split(THINK_CLOSE, 1)
        reasoning = pre.replace(THINK_OPEN, "").strip()
        return {"reasoning_content": reasoning or None, "content": post.strip()}
    return {"reasoning_content": None, "content": raw.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Qwen3 thinking vs fast demo")
    parser.add_argument(
        "--mode",
        choices=("fast", "reasoning"),
        default="fast",
        help="fast = /no_think suffix; reasoning = default thinking",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Override default prompt for the selected mode",
    )
    args = parser.parse_args()

    try:
        from llama_cpp import Llama
    except ImportError:
        print("Install lecture 11 requirements (Vulkan wheel on Intel Arc).", file=sys.stderr)
        return 1

    ensure_hf_token()
    gpu = n_gpu_layers()

    if args.prompt:
        user_text = args.prompt
    elif args.mode == "fast":
        user_text = "What is the capital of France? /no_think"
    else:
        user_text = "If 3x + 7 = 22, what is x?"

    max_tokens = 80 if args.mode == "fast" else 500

    llm = Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=FILENAME,
        n_ctx=4096,
        n_threads=8,
        n_gpu_layers=gpu,
        verbose=False,
    )

    messages = [{"role": "user", "content": user_text}]
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.6 if args.mode == "reasoning" else 0.7,
        top_p=0.95,
    )
    raw = response["choices"][0]["message"]["content"]
    parsed = split_thinking(raw)

    print("MODE:", args.mode)
    print("INPUT:", json.dumps(messages, ensure_ascii=False))
    print("OUTPUT:", json.dumps(parsed, ensure_ascii=False, indent=2))
    print("usage:", response.get("usage"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
