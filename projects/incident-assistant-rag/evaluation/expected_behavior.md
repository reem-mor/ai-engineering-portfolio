# RAG Evaluation Plan

This project validates the IncidentIQ RAG system using five test cases.

## Evaluation Goals

1. Accurate retrieval from FAISS.
2. Grounded answers based only on retrieved context.
3. Correct behavior for irrelevant questions.
4. Incident reasoning output with severity, likely causes, checks, missing information, and escalation.
5. Source transparency through retrieved chunks and filenames.

## Pass Criteria

A test passes if:

- The answer uses the correct retrieved source documents.
- The response does not invent unsupported information.
- The app provides a clear answer or a clear no-context message.
- Incident analysis includes severity and next best action.
- Sources and confidence are returned.
