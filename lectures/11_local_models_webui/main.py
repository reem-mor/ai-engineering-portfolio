"""Local RAG CLI: retrieve, rerank, and generate via llama-server.

Usage:
  python main.py --dry-run
  python main.py --retrieve-only --query "What port does llama-server use?"
  python main.py --query "What embedding model does Open WebUI use?"
  python main.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LECTURE_ROOT = Path(__file__).resolve().parent
DEFAULT_DOC = LECTURE_ROOT / "data" / "local_models_kb.txt"

sys.path.insert(0, str(LECTURE_ROOT / "demos"))
from _env import llama_server_base_url  # noqa: E402

sys.path.insert(0, str(LECTURE_ROOT))
from rag_rerank import (  # noqa: E402
    DEFAULT_RERANK_THRESHOLD,
    DEFAULT_RETRIEVE_K,
    DEFAULT_TOP_K,
    LlamaServerGenerator,
    LocalRagPipeline,
    chunks_to_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local RAG with rerank (lecture 11)")
    parser.add_argument("--dry-run", action="store_true", help="Validate imports and corpus only")
    parser.add_argument(
        "--retrieve-only",
        action="store_true",
        help="Run retrieve + rerank without llama-server generation",
    )
    parser.add_argument("--query", help="Single question to answer")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC, help="Corpus .txt file")
    parser.add_argument("--retrieve-k", type=int, default=DEFAULT_RETRIEVE_K)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--threshold", type=float, default=DEFAULT_RERANK_THRESHOLD)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument(
        "--thinking",
        choices=("on", "off"),
        default="off",
        help="Qwen enable_thinking via chat_template_kwargs",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON output")
    return parser


def ensure_imports() -> None:
    import faiss  # noqa: F401
    import numpy  # noqa: F401
    from sentence_transformers import CrossEncoder, SentenceTransformer  # noqa: F401


def build_pipeline(args: argparse.Namespace) -> LocalRagPipeline:
    generator = None
    if not args.retrieve_only and not args.dry_run:
        generator = LlamaServerGenerator(base_url=llama_server_base_url())

    pipeline = LocalRagPipeline(
        generator=generator,
        retrieve_k=args.retrieve_k,
        top_k=args.top_k,
        threshold=args.threshold,
    )
    pipeline.index_document(args.doc)
    return pipeline


def run_query(pipeline: LocalRagPipeline, args: argparse.Namespace, query: str) -> int:
    if args.retrieve_only:
        retrieved, reranked = pipeline.retrieve_and_rerank(query)
        payload = {
            "query": query,
            "chunks_before_rerank": chunks_to_json(retrieved),
            "chunks_after_rerank": chunks_to_json(reranked),
        }
        if args.json_output:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Query: {query}")
            print("\n--- Before rerank ---")
            for chunk in retrieved:
                print(f"[bi={chunk.bi_score:.3f}] {chunk.content[:120]}...")
            print("\n--- After rerank ---")
            for chunk in reranked:
                score = chunk.rerank_score if chunk.rerank_score is not None else float("nan")
                print(f"[rerank={score:.3f}] {chunk.content[:120]}...")
        return 0

    result = pipeline.answer(
        query,
        max_tokens=args.max_tokens,
        enable_thinking=args.thinking == "on",
    )
    payload = {
        "query": query,
        "answer": result.answer,
        "sources": result.sources,
        "chunks": chunks_to_json(result.chunks),
        "used_context": result.used_context,
    }
    if args.json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Query: {query}")
        print("\n--- Retrieved chunks ---")
        for chunk in result.chunks:
            score = chunk.rerank_score if chunk.rerank_score is not None else float("nan")
            print(f"[{chunk.source} rerank={score:.3f}] {chunk.content[:120]}...")
        print("\n--- Answer ---")
        print(result.answer)
        print(f"\nused_context={result.used_context} sources={result.sources}")
    return 0


def main() -> int:
    args = build_parser().parse_args()

    if not args.doc.is_file():
        print(f"Missing corpus file: {args.doc}", file=sys.stderr)
        return 1

    try:
        ensure_imports()
    except ImportError as exc:
        print(f"Missing dependency: {exc}", file=sys.stderr)
        print(
            "Install: pip install -r lectures/11_local_models_webui/requirements.txt",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        print(f"dry-run OK — corpus: {args.doc.name}, imports OK")
        return 0

    pipeline = build_pipeline(args)

    if args.query:
        return run_query(pipeline, args, args.query)

    print("Local RAG ready. Type 'exit' to quit.\n")
    while True:
        try:
            question = input("Ask: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() == "exit":
            break
        try:
            run_query(pipeline, args, question)
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
