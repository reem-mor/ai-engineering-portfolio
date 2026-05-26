from app.core.config import settings
from app.rag.generator import BaseAnswerGenerator, OpenAIAnswerGenerator
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.schemas.chat_schema import ChatResponse
from app.schemas.search_schema import SearchResult


class RAGPipeline:
    """
    Main Retrieval-Augmented Generation pipeline.

    Flow:
    1. Validate user question.
    2. Retrieve relevant chunks from FAISS.
    3. Filter weak retrieval results.
    4. Build a grounded prompt.
    5. Generate an answer using the LLM.
    6. Return answer, sources, retrieved chunks, confidence, and context status.
    """

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder | None = None,
        answer_generator: BaseAnswerGenerator | None = None,
        score_threshold: float | None = None,
    ) -> None:
        self.retriever = retriever
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.answer_generator = answer_generator or OpenAIAnswerGenerator()
        self.score_threshold = (
            settings.retrieval_score_threshold
            if score_threshold is None
            else score_threshold
        )

    @classmethod
    def create_default(cls) -> "RAGPipeline":
        """
        Create the production/default RAG pipeline.

        This keeps route files clean and prevents every API route from manually
        creating Retriever, PromptBuilder, and OpenAIAnswerGenerator.
        """
        return cls(
            retriever=Retriever(),
            prompt_builder=PromptBuilder(),
            answer_generator=OpenAIAnswerGenerator(),
        )

    def answer_question(self, question: str, top_k: int = 5) -> ChatResponse:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError("Question cannot be empty.")

        if top_k < settings.top_k_min or top_k > settings.top_k_max:
            raise ValueError(
                f"top_k must be between {settings.top_k_min} and {settings.top_k_max}."
            )

        retrieved_chunks = self.retriever.retrieve(
            question=clean_question,
            top_k=top_k,
        )

        relevant_chunks = self._filter_relevant_chunks(retrieved_chunks)

        if not relevant_chunks:
            return ChatResponse(
                answer="The knowledge base does not contain enough information to answer this question.",
                sources=[],
                retrieved_chunks=[],
                confidence="none",
                used_context=False,
            )

        prompt = self.prompt_builder.build(
            question=clean_question,
            retrieved_chunks=relevant_chunks,
        )

        answer = self.answer_generator.generate(prompt)

        sources = sorted({chunk.source_file for chunk in relevant_chunks})

        return ChatResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=relevant_chunks,
            confidence=self._calculate_confidence(relevant_chunks),
            used_context=True,
        )

    def _filter_relevant_chunks(
        self,
        retrieved_chunks: list[SearchResult],
    ) -> list[SearchResult]:
        return [
            chunk for chunk in retrieved_chunks if chunk.score >= self.score_threshold
        ]

    @staticmethod
    def _calculate_confidence(chunks: list[SearchResult]) -> str:
        if not chunks:
            return "none"

        best_score = max(chunk.score for chunk in chunks)

        if best_score >= 0.75:
            return "high"

        if best_score >= 0.5:
            return "medium"

        return "low"
