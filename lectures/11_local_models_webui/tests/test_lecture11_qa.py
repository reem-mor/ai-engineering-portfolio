"""QA tests for lecture 11 — structure, examples, imports (no GPU required)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

LECTURE = Path(__file__).resolve().parents[1]
DEMOS = LECTURE / "demos"
EXAMPLES_IO = LECTURE / "examples" / "io"
PYTHON = sys.executable

EXPECTED_IO_FILES = [
    "qwen25_factual.json",
    "qwen25_reasoning.json",
    "qwen3_fast_no_think.json",
    "qwen3_reasoning_thinking.json",
    "huggingface_download.json",
    "llama_server_api.json",
    "ragas_eval_sample.json",
    "rag_rerank_sample.json",
]

EXPECTED_ROOT_FILES = [
    "rag_rerank.py",
    "main.py",
]

EXPECTED_DATA_FILES = [
    "local_models_kb.txt",
]

EXPECTED_DEMOS = [
    "_env.py",
    "qwen25_chat.py",
    "qwen3_reasoning_chat.py",
    "qwen36_vision_chat.py",
    "huggingface_model_info.py",
    "llama_server_chat.py",
    "ragas_eval_smoke.py",
]


@pytest.mark.parametrize("name", EXPECTED_IO_FILES)
def test_example_io_json_valid(name: str) -> None:
    path = EXAMPLES_IO / name
    assert path.is_file(), f"missing {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "input" in data or "interface" in data


@pytest.mark.parametrize("name", EXPECTED_DEMOS)
def test_demo_scripts_exist(name: str) -> None:
    assert (DEMOS / name).is_file()


@pytest.mark.parametrize("name", EXPECTED_ROOT_FILES)
def test_root_scripts_exist(name: str) -> None:
    assert (LECTURE / name).is_file()


@pytest.mark.parametrize("name", EXPECTED_DATA_FILES)
def test_data_files_exist(name: str) -> None:
    assert (LECTURE / "data" / name).is_file()


def test_requirements_lists_ragas() -> None:
    text = (LECTURE / "requirements.txt").read_text(encoding="utf-8")
    assert "ragas" in text
    assert "llama-cpp-python" in text
    assert "sentence-transformers" in text
    assert "faiss-cpu" in text


def test_ragas_import() -> None:
    pytest.importorskip("ragas")
    from ragas import EvaluationDataset  # noqa: F401


def test_ragas_dry_run_cli() -> None:
    result = subprocess.run(
        [PYTHON, "ragas_eval_smoke.py", "--dry-run"],
        cwd=DEMOS,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "dry-run OK" in result.stdout


def test_huggingface_model_info_no_download() -> None:
    result = subprocess.run(
        [PYTHON, "huggingface_model_info.py"],
        cwd=DEMOS,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "GGUF files in repo" in result.stdout


def test_env_helpers() -> None:
    sys.path.insert(0, str(DEMOS))
    try:
        import _env as env_mod  # noqa: PLC0415
    finally:
        sys.path.pop(0)
    assert env_mod.EXAMPLES_IO.is_dir()
    assert env_mod.llama_server_base_url().endswith("/v1")


def test_split_thinking_helper() -> None:
    sys.path.insert(0, str(DEMOS))
    try:
        import qwen3_reasoning_chat as mod  # noqa: PLC0415
    finally:
        sys.path.pop(0)
    raw = mod.THINK_OPEN + "step one" + mod.THINK_CLOSE + "\nFinal answer."
    parsed = mod.split_thinking(raw)
    assert parsed["reasoning_content"] == "step one"
    assert parsed["content"] == "Final answer."


def test_rerank_orders_by_score() -> None:
    sys.path.insert(0, str(LECTURE))
    try:
        from rag_rerank import CrossEncoderReranker, RetrievedChunk  # noqa: PLC0415
    finally:
        sys.path.pop(0)

    class FakeCrossEncoder:
        def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
            return [0.2, 0.9, 0.5][: len(pairs)]

    chunks = [
        RetrievedChunk(content="low", source="doc.txt", bi_score=0.8),
        RetrievedChunk(content="high", source="doc.txt", bi_score=0.7),
        RetrievedChunk(content="mid", source="doc.txt", bi_score=0.6),
    ]
    reranker = CrossEncoderReranker(model=FakeCrossEncoder())
    ranked = reranker.rerank("query", chunks, top_k=2)
    assert [item.content for item in ranked] == ["high", "mid"]
    assert ranked[0].rerank_score == 0.9


def test_refusal_below_threshold() -> None:
    sys.path.insert(0, str(LECTURE))
    try:
        from rag_rerank import (  # noqa: PLC0415
            NO_CONTEXT_MESSAGE,
            LocalRagPipeline,
            RetrievedChunk,
        )
    finally:
        sys.path.pop(0)

    class FakeIndex:
        ready = True

        def retrieve(self, query: str, *, k: int = 10) -> list[RetrievedChunk]:
            return [RetrievedChunk(content="weak match", source="doc.txt", bi_score=0.4)]

    class FakeReranker:
        def rerank(
            self,
            query: str,
            chunks: list[RetrievedChunk],
            *,
            top_k: int = 3,
        ) -> list[RetrievedChunk]:
            return [
                RetrievedChunk(
                    content=chunk.content,
                    source=chunk.source,
                    bi_score=chunk.bi_score,
                    rerank_score=0.1,
                )
                for chunk in chunks
            ]

    class FailGenerator:
        def generate(self, *args, **kwargs) -> str:
            raise AssertionError("LLM should not be called when below threshold")

    pipeline = LocalRagPipeline(
        bi_index=FakeIndex(),  # type: ignore[arg-type]
        reranker=FakeReranker(),  # type: ignore[arg-type]
        generator=FailGenerator(),  # type: ignore[arg-type]
        threshold=0.35,
    )
    result = pipeline.answer("irrelevant question")
    assert result.used_context is False
    assert result.answer == NO_CONTEXT_MESSAGE
    assert result.sources == []


def test_main_dry_run_cli() -> None:
    result = subprocess.run(
        [PYTHON, "main.py", "--dry-run"],
        cwd=LECTURE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "dry-run OK" in result.stdout


def test_main_retrieve_only() -> None:
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")
    result = subprocess.run(
        [
            PYTHON,
            "main.py",
            "--retrieve-only",
            "--query",
            "What port does llama-server use?",
        ],
        cwd=LECTURE,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "After rerank" in result.stdout
    assert "8080" in result.stdout
