from app.schemas.search_schema import SearchResult


class IncidentPromptBuilder:
    def build(self, description: str, severity: str, retrieved_chunks: list[SearchResult], affected_service: str | None = None, environment: str | None = None) -> str:
        clean_description = description.strip()
        if not clean_description:
            raise ValueError("Incident description cannot be empty.")
        context = self._format_context(retrieved_chunks) if retrieved_chunks else "No relevant context was retrieved from the knowledge base."
        return f"""
You are an Incident Assistant for technical operations.

Analyze the incident using only the retrieved knowledge-base context.
Do not invent commands, owners, root causes, or procedures.
If the context is not enough, clearly say what information is missing.

Return the answer in this exact JSON format:
{{
  "incident_summary": "short summary",
  "severity": "{severity}",
  "likely_causes": ["cause 1", "cause 2"],
  "recommended_checks": ["check 1", "check 2"],
  "missing_information": ["missing item 1", "missing item 2"],
  "next_best_action": "single safest next action",
  "escalation_recommendation": "who to escalate to and when"
}}

Incident details:
Affected service: {affected_service or "Not provided"}
Environment: {environment or "Not provided"}
Initial severity estimate: {severity}
Description: {clean_description}

Retrieved context:
{context}
""".strip()

    def _format_context(self, retrieved_chunks: list[SearchResult]) -> str:
        return "\n\n".join(
            f"[Source {index}]\nFile: {chunk.source_file}\nChunk ID: {chunk.chunk_id}\nScore: {chunk.score:.4f}\nText:\n{chunk.text}"
            for index, chunk in enumerate(retrieved_chunks, start=1)
        )
