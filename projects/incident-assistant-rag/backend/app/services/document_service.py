import json
from pathlib import Path

from app.core.config import settings
from app.rag.chunker import TextChunker
from app.rag.document_loader import DocumentLoader
from app.rag.embeddings import BaseEmbeddingProvider, OpenAIEmbeddingProvider
from app.rag.faiss_store import FaissVectorStore
from app.rag.text_cleaner import TextCleaner
from app.schemas.chunk_schema import DocumentChunk
from app.schemas.embedding_schema import EmbeddedChunk


class DocumentService:
    """
    Service responsible for the full document indexing flow.

    Flow:
    1. Load document content.
    2. Clean text.
    3. Split text into chunks.
    4. Create embeddings.
    5. Save processed artifacts.
    6. Build and save the FAISS index.
    """

    def __init__(
        self,
        loader: DocumentLoader | None = None,
        cleaner: TextCleaner | None = None,
        chunker: TextChunker | None = None,
        embedding_provider: BaseEmbeddingProvider | None = None,
        vector_store: FaissVectorStore | None = None,
    ) -> None:
        self.loader = loader or DocumentLoader()
        self.cleaner = cleaner or TextCleaner()
        self.chunker = chunker or TextChunker()
        self.embedding_provider = embedding_provider or OpenAIEmbeddingProvider()
        self.vector_store = vector_store or FaissVectorStore()

    def extract_and_clean(self, file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        if file_path.suffix.lower() not in settings.allowed_file_extensions:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        raw_text = self.loader.load(file_path)
        cleaned_text = self.cleaner.clean(raw_text)

        if not cleaned_text.strip():
            raise ValueError(f"No readable text extracted from file: {file_path.name}")

        return cleaned_text

    def chunk_text(self, text: str, source_file: str) -> list[DocumentChunk]:
        if not text.strip():
            raise ValueError(f"Cannot chunk empty text from file: {source_file}")

        chunks = self.chunker.chunk(text, source_file)

        if not chunks:
            raise ValueError(f"No chunks created from file: {source_file}")

        return chunks

    def embed_chunks(self, chunks: list[DocumentChunk]) -> list[EmbeddedChunk]:
        if not chunks:
            raise ValueError("Cannot embed an empty chunk list.")

        embedded_chunks = self.embedding_provider.embed_chunks(chunks)

        if not embedded_chunks:
            raise ValueError("Embedding provider returned no embedded chunks.")

        return embedded_chunks

    def save_processed_text(self, file_path: Path, text: str) -> None:
        settings.processed_data_dir.mkdir(parents=True, exist_ok=True)

        output_path = settings.processed_data_dir / f"{file_path.stem}.txt"
        output_path.write_text(text, encoding="utf-8")

    def save_chunks(self, file_path: Path, chunks: list[DocumentChunk]) -> None:
        settings.chunks_data_dir.mkdir(parents=True, exist_ok=True)

        rows = [chunk.model_dump() for chunk in chunks]
        output_path = settings.chunks_data_dir / f"{file_path.stem}.json"

        output_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_embedded_chunks(
        self,
        file_path: Path,
        embedded_chunks: list[EmbeddedChunk],
    ) -> None:
        settings.embeddings_data_dir.mkdir(parents=True, exist_ok=True)

        rows = [item.model_dump() for item in embedded_chunks]
        output_path = settings.embeddings_data_dir / f"{file_path.stem}.json"

        output_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def process_embed_and_index_file(self, file_path: Path) -> None:
        self.process_embed_and_index_files([file_path])

    def process_embed_and_index_files(self, file_paths: list[Path]) -> None:
        if not file_paths:
            raise ValueError("No files provided for indexing.")

        all_embedded_chunks: list[EmbeddedChunk] = []

        for file_path in file_paths:
            if file_path.suffix.lower() not in settings.allowed_file_extensions:
                raise ValueError(f"Unsupported file type: {file_path.name}")

            cleaned_text = self.extract_and_clean(file_path)
            self.save_processed_text(file_path, cleaned_text)

            chunks = self.chunk_text(cleaned_text, file_path.name)
            self.save_chunks(file_path, chunks)

            embedded_chunks = self.embed_chunks(chunks)
            self.save_embedded_chunks(file_path, embedded_chunks)

            all_embedded_chunks.extend(embedded_chunks)

        if not all_embedded_chunks:
            raise ValueError("No embedded chunks were created.")

        self.vector_store.build_and_save(all_embedded_chunks)

    def list_supported_files(self, directory: Path) -> list[Path]:
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        return sorted(
            file_path
            for file_path in directory.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower() in settings.allowed_file_extensions
        )
