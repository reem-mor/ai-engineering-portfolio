import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.rag.embeddings import FakeEmbeddingProvider, OpenAIEmbeddingProvider
from app.rag.faiss_store import FaissVectorStore
from app.rag.generator import (
    FakeAnswerGenerator,
    FakeIncidentAnswerGenerator,
    OpenAIAnswerGenerator,
)
from app.rag.prompt_builder import PromptBuilder
from app.rag.rag_pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.reasoning.incident_reasoner import IncidentReasoner
from app.services.document_service import DocumentService

QUESTIONS_PATH = PROJECT_ROOT / "evaluation" / "test_questions.json"
RESULTS_JSON_PATH = PROJECT_ROOT / "evaluation" / "evaluation_results.json"
RESULTS_MD_PATH = PROJECT_ROOT / "evaluation" / "evaluation_results.md"
OFFLINE_EMBED_DIM = 16


def load_questions() -> list[dict[str, Any]]:
    return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def _use_offline_mode() -> bool:
    key = (os.environ.get("OPENAI_API_KEY") or settings.openai_api_key or "").strip()
    return not key or key.startswith("sk-test-placeholder")


def ensure_sample_index(offline: bool) -> None:
    index_path = settings.faiss_index_dir / settings.faiss_index_file
    metadata_path = settings.faiss_index_dir / settings.faiss_metadata_file
    if index_path.is_file() and metadata_path.is_file() and not offline:
        return

    if offline:
        provider = FakeEmbeddingProvider(dimensions=OFFLINE_EMBED_DIM)
    else:
        provider = OpenAIEmbeddingProvider()

    service = DocumentService(
        embedding_provider=provider,
        vector_store=FaissVectorStore(),
    )
    files = service.list_supported_files(settings.sample_documents_dir)
    if not files:
        raise FileNotFoundError(
            f"No sample documents found in {settings.sample_documents_dir}"
        )
    service.process_embed_and_index_files(files)


def build_retriever(offline: bool) -> Retriever:
    vector_store = FaissVectorStore()
    vector_store.load()
    if offline:
        return Retriever(
            vector_store=vector_store,
            embedding_provider=FakeEmbeddingProvider(dimensions=OFFLINE_EMBED_DIM),
        )
    return Retriever(
        vector_store=vector_store,
        embedding_provider=OpenAIEmbeddingProvider(),
    )


def check_keywords(text: str, expected_keywords: list[str]) -> dict[str, Any]:
    lower_text = text.lower()
    found = [keyword for keyword in expected_keywords if keyword.lower() in lower_text]
    missing = [keyword for keyword in expected_keywords if keyword.lower() not in lower_text]
    return {"found": found, "missing": missing, "passed": len(missing) == 0}


def main() -> None:
    offline = _use_offline_mode()
    if offline:
        print("Offline evaluation: fake embeddings and generators (no OpenAI calls).")
    ensure_sample_index(offline=offline)

    questions = load_questions()
    retriever = build_retriever(offline=offline)
    if offline:
        answer_generator = FakeAnswerGenerator()
        incident_generator = FakeIncidentAnswerGenerator()
        score_threshold = 0.0
    else:
        answer_generator = OpenAIAnswerGenerator()
        incident_generator = OpenAIAnswerGenerator()
        score_threshold = settings.retrieval_score_threshold

    pipeline = RAGPipeline(
        retriever=retriever,
        prompt_builder=PromptBuilder(),
        answer_generator=answer_generator,
        score_threshold=score_threshold,
    )
    reasoner = IncidentReasoner(
        rag_pipeline_or_retriever=retriever,
        answer_generator=incident_generator,
        score_threshold=score_threshold,
    )
    results = []
    for question in questions:
        if question["type"] == "incident_reasoning":
            response = reasoner.analyze(question["question"], question.get("affected_service"), question.get("environment"), top_k=5)
            combined_text = " ".join([response.incident_summary, response.severity, " ".join(response.recommended_checks), response.next_best_action, response.escalation_recommendation])
            actual_sources = response.sources
            result = {"id": question["id"], "type": question["type"], "question": question["question"], "answer": response.incident_summary, "confidence": response.confidence, "used_context": response.used_context, "actual_sources": actual_sources, "expected_sources": question.get("expected_sources", []), "keyword_check": check_keywords(combined_text, question.get("expected_keywords", []))}
        else:
            response = pipeline.answer_question(question["question"], top_k=5)
            actual_sources = response.sources
            result = {"id": question["id"], "type": question["type"], "question": question["question"], "answer": response.answer, "confidence": response.confidence, "used_context": response.used_context, "actual_sources": actual_sources, "expected_sources": question.get("expected_sources", []), "keyword_check": check_keywords(response.answer, question.get("expected_keywords", []))}
        expected_sources = result["expected_sources"]
        source_match = any(source in result["actual_sources"] for source in expected_sources) if expected_sources else len(result["actual_sources"]) == 0
        result["passed"] = bool(result["keyword_check"]["passed"] and source_match)
        results.append(result)
    RESULTS_JSON_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    passed = sum(1 for item in results if item["passed"])
    mode_line = "Offline (fake embeddings/generators)" if offline else "Live (OpenAI)"
    lines = [
        "# RAG Evaluation Results",
        "",
        f"Mode: {mode_line}",
        f"Passed: {passed}/{len(results)}",
        "",
    ]
    for result in results:
        lines.extend([f"## Test {result['id']} - {'PASS' if result['passed'] else 'FAIL'}", "", f"Question: {result['question']}", "", f"Confidence: {result['confidence']}", "", f"Used context: {result['used_context']}", "", f"Actual sources: {result['actual_sources']}", "", f"Missing keywords: {result['keyword_check']['missing']}", "", result["answer"], ""])
    RESULTS_MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Evaluation complete: {passed}/{len(results)} passed")


if __name__ == "__main__":
    main()
