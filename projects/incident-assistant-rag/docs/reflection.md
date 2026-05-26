# Reflection

I built IncidentIQ, a full-stack RAG application for technical incident assistance. I chose this topic because incident investigation is a realistic operational problem where RAG can help teams find the correct runbook, understand likely causes, and choose safe next actions.

The most important part of the project was building the full RAG pipeline from documents to answer generation. I learned how documents are loaded, cleaned, chunked, embedded, stored in FAISS, retrieved semantically, and injected into a prompt.

The project also taught me that a RAG system must handle uncertainty. For example, when a user asks an irrelevant question, the system should not invent an answer. It should clearly say that the knowledge base does not contain enough information.

The incident reasoning endpoint made the project more useful than a basic chatbot. It returns severity, likely causes, recommended checks, missing information, next best action, and escalation recommendation.

In production, I would improve the project by moving ingestion to a background workflow system such as Inngest or Celery, adding retries and rate limiting for OpenAI calls, adding structured observability, and replacing local FAISS with Qdrant for scalable vector search.
