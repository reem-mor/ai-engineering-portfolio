from abc import ABC, abstractmethod
import hashlib
import math

from openai import OpenAI

from app.core.config import settings
from app.schemas.chunk_schema import DocumentChunk
from app.schemas.embedding_schema import EmbeddedChunk


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_chunks(self, chunks: list[DocumentChunk]) -> list[EmbeddedChunk]:
        return [EmbeddedChunk(chunk=chunk, embedding=self.embed_text(chunk.text)) for chunk in chunks]


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.embedding_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings.")
        self.client = OpenAI(api_key=self.api_key)

    def embed_text(self, text: str) -> list[float]:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Text cannot be empty for embedding.")
        response = self.client.embeddings.create(model=self.model, input=clean_text)
        return response.data[0].embedding


class FakeEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, dimensions: int = 16) -> None:
        self.dimensions = dimensions

    def embed_text(self, text: str) -> list[float]:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Text cannot be empty for embedding.")
        digest = hashlib.sha256(clean_text.encode("utf-8")).digest()
        values = []
        for index in range(self.dimensions):
            values.append((digest[index % len(digest)] / 255.0) + 0.001)
        norm = math.sqrt(sum(value * value for value in values))
        return [value / norm for value in values]
