import pytest

from app.rag.embeddings import FakeEmbeddingProvider


def test_fake_embedding_provider_is_deterministic():
    provider = FakeEmbeddingProvider(dimensions=8)
    assert provider.embed_text("hello") == provider.embed_text("hello")


def test_fake_embedding_provider_rejects_empty_text():
    provider = FakeEmbeddingProvider(dimensions=8)
    with pytest.raises(ValueError):
        provider.embed_text(" ")


def test_fake_embedding_dimensions_affect_vector_length():
    short_v = FakeEmbeddingProvider(dimensions=4).embed_text("hello")
    long_v = FakeEmbeddingProvider(dimensions=12).embed_text("hello")
    assert len(short_v) == 4 and len(long_v) == 12
