# RAG Pipeline

The RAG pipeline converts documents into searchable vectors and uses retrieved context to answer user questions.

## Ingestion Flow

```text
Document
  -> load text
  -> clean text
  -> split into chunks
  -> generate embeddings
  -> store in FAISS
```

## Query Flow

```text
User question
  -> embed question
  -> search FAISS
  -> filter weak matches
  -> build grounded prompt
  -> generate answer
  -> return answer and sources
```

## Hallucination Controls

The project reduces hallucination with:

- strict prompts
- score threshold filtering
- no-context response
- returned sources
- confidence field
- irrelevant question evaluation

## Why Custom Pipeline

A custom pipeline is used instead of hiding everything behind a framework. This makes the project easier to explain and proves understanding of loading, cleaning, chunking, embedding, retrieval, prompting, and answer generation.
