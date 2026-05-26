from app.schemas.search_schema import SearchResult


class PromptBuilder:
    def build(self, question: str, retrieved_chunks: list[SearchResult]) -> str:
        clean_question = question.strip()
        if not clean_question:
            raise ValueError("Question cannot be empty.")
        if not retrieved_chunks:
            return self._build_no_context_prompt(clean_question)
        context = self._format_context(retrieved_chunks)
        return f"""
You are an Incident Assistant RAG system.

Your task:
Answer the user's question using only the context below.

Rules:
- Use only the provided context.
- Do not invent commands, owners, causes, or procedures.
- If the context is not enough, say that the knowledge base does not contain enough information.
- Give a clear, practical answer.
- Do not fabricate source filenames.

Context:
{context}

User question:
{clean_question}

Answer:
""".strip()

    def _format_context(self, retrieved_chunks: list[SearchResult]) -> str:
        parts = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            parts.append(f"""
[Source {index}]
File: {chunk.source_file}
Chunk ID: {chunk.chunk_id}
Score: {chunk.score:.4f}
Text:
{chunk.text}
""".strip())
        return "\n\n".join(parts)

    def _build_no_context_prompt(self, question: str) -> str:
        return f"""
You are an Incident Assistant RAG system.

The knowledge base did not return relevant context.

User question:
{question}

Answer:
Say that the knowledge base does not contain enough information to answer this question.
Do not invent information.
""".strip()
