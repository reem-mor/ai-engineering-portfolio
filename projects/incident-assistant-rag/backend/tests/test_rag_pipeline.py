import pytest

from app.rag.generator import FakeAnswerGenerator
from app.rag.rag_pipeline import RAGPipeline
from app.schemas.search_schema import SearchResult


class FakeRetriever:
    def __init__(self, results):
        self.results = results
    def retrieve(self, question: str, top_k: int = 5):
        return self.results[:top_k]


def test_rag_pipeline_filters_low_score_chunks():
    pipeline = RAGPipeline(FakeRetriever([SearchResult(chunk_id="x", source_file="x.md", chunk_index=0, text="weak", score=0.1)]), answer_generator=FakeAnswerGenerator(), score_threshold=0.25)
    response = pipeline.answer_question("question")
    assert response.used_context is False
    assert response.confidence == "none"


def test_rag_pipeline_high_confidence():
    pipeline = RAGPipeline(FakeRetriever([SearchResult(chunk_id="x", source_file="x.md", chunk_index=0, text="strong", score=0.9)]), answer_generator=FakeAnswerGenerator(), score_threshold=0.25)
    response = pipeline.answer_question("question")
    assert response.used_context is True
    assert response.confidence == "high"


def test_rag_pipeline_rejects_empty_question():
    pipeline = RAGPipeline(FakeRetriever([]), answer_generator=FakeAnswerGenerator())
    with pytest.raises(ValueError):
        pipeline.answer_question(" ")


def test_rag_pipeline_medium_confidence_band():
    pipeline = RAGPipeline(FakeRetriever([SearchResult(chunk_id="m", source_file="m.md", chunk_index=0, text="mid", score=0.6)]), answer_generator=FakeAnswerGenerator(), score_threshold=0.25)
    response = pipeline.answer_question("anything")
    assert response.used_context is True
    assert response.confidence == "medium"


def test_rag_pipeline_low_confidence_band():
    pipeline = RAGPipeline(FakeRetriever([SearchResult(chunk_id="l", source_file="l.md", chunk_index=0, text="low", score=0.41)]), answer_generator=FakeAnswerGenerator(), score_threshold=0.25)
    response = pipeline.answer_question("anything")
    assert response.used_context is True
    assert response.confidence == "low"
