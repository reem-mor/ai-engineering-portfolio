"""Call local llama-server OpenAI-compatible API (Qwen best-practice kwargs).

Prerequisite: scripts/start_llama_server.ps1 (or manual llama_cpp.server on :8080)

See examples/io/llama_server_api.json for recorded I/O.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from _env import llama_server_base_url


def main() -> int:
    parser = argparse.ArgumentParser(description="llama-server chat completion client")
    parser.add_argument("--prompt", default="What is the capital of France?")
    parser.add_argument(
        "--thinking",
        choices=("on", "off"),
        default="off",
        help="Qwen3 enable_thinking via chat_template_kwargs",
    )
    parser.add_argument("--max-tokens", type=int, default=120)
    args = parser.parse_args()

    base = llama_server_base_url()
    url = f"{base.rstrip('/')}/chat/completions"

    body = {
        "model": "local",
        "messages": [{"role": "user", "content": args.prompt}],
        "max_tokens": args.max_tokens,
        "chat_template_kwargs": {"enable_thinking": args.thinking == "on"},
    }

    print("INPUT:", json.dumps(body, indent=2, ensure_ascii=False))
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        print(f"Cannot reach llama-server at {url}: {exc}", file=sys.stderr)
        print("Start: .\\lectures\\11_local_models_webui\\scripts\\start_llama_server.ps1", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode()[:500]}", file=sys.stderr)
        return 1

    msg = data["choices"][0]["message"]
    print("OUTPUT keys:", list(msg.keys()))
    print("OUTPUT:", json.dumps(msg, ensure_ascii=False, indent=2))
    print("usage:", data.get("usage"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
