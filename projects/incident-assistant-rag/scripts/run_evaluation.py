import json
from pathlib import Path
from typing import Any

from app.rag.faiss_store import FaissVectorStore
from app.rag.prompt_builder import PromptBuilder
from app.rag.rag_pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.rag.embeddings import OpenAIEmbeddingProvider
from app.rag.generator import OpenAIAnswerGenerator
from app.reasoning.incident_reasoner import IncidentReasoner

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = PROJECT_ROOT / "evaluation" / "test_questions.json"
RESULTS_JSON_PATH = PROJECT_ROOT / "evaluation" / "evaluation_results.json"
RESULTS_MD_PATH = PROJECT_ROOT / "evaluation" / "evaluation_results.md"


def load_questions() -> list[dict[str, Any]]:
    return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def build_retriever() -> Retriever:
    vector_store = FaissVectorStore()
    vector_store.load()
    return Retriever(vector_store=vector_store, embedding_provider=OpenAIEmbeddingProvider())


def check_keywords(text: str, expected_keywords: list[str]) -> dict[str, Any]:
    lower_text = text.lower()
    found = [keyword for keyword in expected_keywords if keyword.lower() in lower_text]
    missing = [keyword for keyword in expected_keywords if keyword.lower() not in lower_text]
    return {"found": found, "missing": missing, "passed": len(missing) == 0}


def main() -> None:
    questions = load_questions()
    retriever = build_retriever()
    pipeline = RAGPipeline(retriever=retriever, prompt_builder=PromptBuilder(), answer_generator=OpenAIAnswerGenerator())
    reasoner = IncidentReasoner(retriever=retriever, answer_generator=OpenAIAnswerGenerator())
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
    lines = ["# RAG Evaluation Results", "", f"Passed: {passed}/{len(results)}", ""]
    for result in results:
        lines.extend([f"## Test {result['id']} - {'PASS' if result['passed'] else 'FAIL'}", "", f"Question: {result['question']}", "", f"Confidence: {result['confidence']}", "", f"Used context: {result['used_context']}", "", f"Actual sources: {result['actual_sources']}", "", f"Missing keywords: {result['keyword_check']['missing']}", "", result["answer"], ""])
    RESULTS_MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Evaluation complete: {passed}/{len(results)} passed")


if __name__ == "__main__":
    main()
