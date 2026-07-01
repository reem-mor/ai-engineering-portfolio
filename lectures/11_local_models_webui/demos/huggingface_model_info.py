"""Hugging Face Hub — list repo files and resolve a GGUF download path.

See examples/io/huggingface_download.json for recorded I/O.
"""

from __future__ import annotations

import argparse
import json
import sys

from _env import ensure_hf_token, hf_token


def main() -> int:
    parser = argparse.ArgumentParser(description="Hugging Face model info / download path")
    parser.add_argument(
        "--repo",
        default="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        help="Hugging Face repo id",
    )
    parser.add_argument(
        "--filename",
        default="qwen2.5-1.5b-instruct-q4_k_m.gguf",
        help="GGUF filename to resolve",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download file to HF cache (requires network)",
    )
    args = parser.parse_args()

    try:
        from huggingface_hub import hf_hub_download, list_repo_files
    except ImportError:
        print("Install: pip install huggingface_hub", file=sys.stderr)
        return 1

    ensure_hf_token()
    token = hf_token()

    print("INPUT:", json.dumps({"repo_id": args.repo, "filename": args.filename}, indent=2))
    print("HF_TOKEN set:", bool(token))

    files = list_repo_files(args.repo, token=token)
    gguf_files = [f for f in files if f.endswith(".gguf")]
    print("\nGGUF files in repo:", json.dumps(gguf_files[:10], indent=2))
    if len(gguf_files) > 10:
        print(f"  ... and {len(gguf_files) - 10} more")

    if args.filename not in files:
        print(f"Warning: {args.filename} not in repo file list.", file=sys.stderr)
        return 1

    if args.download:
        path = hf_hub_download(args.repo, args.filename, token=token)
        import os

        print("\nOUTPUT:", json.dumps({"path": path, "size_bytes": os.path.getsize(path)}, indent=2))
    else:
        print("\nOUTPUT: pass --download to fetch and print cache path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
