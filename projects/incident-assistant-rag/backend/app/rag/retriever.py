from app.rag.embeddings import BaseEmbeddingProvider, OpenAIEmbeddingProvider
from app.rag.faiss_store import FaissVectorStore
from app.schemas.search_schema import SearchResult


class Retriever:
    """
    Retrieval layer for the RAG pipeline.

    Responsibilities:
    1. Validate the user query.
    2. Convert the query to an embedding.
    3. Search the FAISS vector store.
    4. Return ranked SearchResult objects.
    """

    def __init__(
        self,
        vector_store: FaissVectorStore | None = None,
        embedding_provider: BaseEmbeddingProvider | None = None,
    ) -> None:
        self.vector_store = vector_store or FaissVectorStore()
        self.embedding_provider = embedding_provider or OpenAIEmbeddingProvider()

    def retrieve(self, question: str, top_k: int = 5) -> list[SearchResult]:
        clean_question = " ".join(question.strip().split())

        if not clean_question:
            raise ValueError("Question cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if (
            not self.vector_store.index_path.exists()
            or not self.vector_store.metadata_path.exists()
        ):
            raise FileNotFoundError("FAISS index is not loaded.")

        query_embedding = self.embedding_provider.embed_text(clean_question)

        if not query_embedding:
            raise ValueError("Embedding provider returned an empty query embedding.")

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )
