"""RAGAS evaluation smoke test — validate dataset; optional live eval with OpenAI.

See examples/io/ragas_eval_sample.json for sample I/O.

Usage:
  python demos/ragas_eval_smoke.py --dry-run     # no LLM calls (CI-safe)
  python demos/ragas_eval_smoke.py --eval        # needs OPENAI_API_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from _env import EXAMPLES_IO, REPO_ROOT

SAMPLE_PATH = EXAMPLES_IO / "ragas_eval_sample.json"


def load_samples() -> list[dict]:
    data = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    return data["input"]["samples"]


def build_dataset(samples: list[dict]):
    from ragas import EvaluationDataset

    return EvaluationDataset.from_list(samples)


def run_eval(dataset) -> dict:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas import evaluate
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import answer_relevancy, faithfulness

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        raise RuntimeError("Set OPENAI_API_KEY in repo-root .env for --eval")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = LangchainLLMWrapper(ChatOpenAI(model=model, temperature=0))
    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embeddings,
    )
    return result.to_pandas().mean(numeric_only=True).to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="RAGAS lecture smoke test")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate dataset and imports only (default if --eval omitted)",
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run faithfulness + answer_relevancy with OPENAI_API_KEY",
    )
    args = parser.parse_args()

    if not SAMPLE_PATH.is_file():
        print(f"Missing {SAMPLE_PATH}", file=sys.stderr)
        return 1

    try:
        import ragas  # noqa: F401
    except ImportError as exc:
        print(f"ragas not installed: {exc}", file=sys.stderr)
        print("pip install -r lectures/11_local_models_webui/requirements.txt", file=sys.stderr)
        return 1

    samples = load_samples()
    dataset = build_dataset(samples)

    print("INPUT samples:", json.dumps(samples, indent=2, ensure_ascii=False)[:800], "...")
    print(f"Dataset rows: {len(dataset)}")
    print("ragas import: OK")

    if args.eval:
        load_dotenv = __import__("dotenv", fromlist=["load_dotenv"]).load_dotenv
        load_dotenv(REPO_ROOT / ".env")
        scores = run_eval(dataset)
        print("OUTPUT scores:", json.dumps(scores, indent=2))
    else:
        print("OUTPUT: dry-run OK (pass --eval to score with OpenAI)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
