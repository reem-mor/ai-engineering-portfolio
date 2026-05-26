from app.core.config import settings
from app.schemas.chunk_schema import DocumentChunk


class TextChunker:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None) -> None:
        # Do not use `chunk_size or default`: 0 is valid input and must not fall back to settings.
        self.chunk_size = settings.chunk_size if chunk_size is None else chunk_size
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

    def chunk(self, text: str, source_file: str) -> list[DocumentChunk]:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Text cannot be empty.")

        chunks: list[DocumentChunk] = []
        start = 0
        index = 0

        while start < len(clean_text):
            end = min(start + self.chunk_size, len(clean_text))
            candidate = clean_text[start:end]

            if end < len(clean_text):
                split_at = max(candidate.rfind("\n\n"), candidate.rfind(". "))
                if split_at > self.chunk_size // 2:
                    end = start + split_at + 1
                    candidate = clean_text[start:end]

            candidate = candidate.strip()
            if candidate:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{source_file}::chunk-{index}",
                        source_file=source_file,
                        chunk_index=index,
                        text=candidate,
                    )
                )
                index += 1

            if end >= len(clean_text):
                break

            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = end
            start = next_start

        return chunks
