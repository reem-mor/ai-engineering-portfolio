import os
import sys
import time
import faiss
import numpy as np
import nltk

from google import genai
from google.genai import types
from huggingface_hub import InferenceClient
from nltk.tokenize import sent_tokenize


# ==========================
# Configuration
# ==========================

DATA_FOLDER = "data"

# Hugging Face embedding model running in the cloud
HF_EMBEDDING_MODEL = "ibm-granite/granite-embedding-97m-multilingual-r2"

# You can also try this one:
# HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

GEMINI_MODEL = "gemini-3-flash-preview"

TOP_K = 3
BATCH_SIZE = 8


# ==========================
# API Clients
# ==========================

def create_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("ERROR: GEMINI_API_KEY is missing.")
        print('PowerShell: $env:GEMINI_API_KEY="AIzaSyD2fyni9M_m9wzYLODr2drek-s_t-C49xA"')
        sys.exit(1)

    return genai.Client(api_key=api_key)


def create_huggingface_client():
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("ERROR: HF_TOKEN is missing.")
        print('PowerShell: $env:HF_TOKEN="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"')
        sys.exit(1)

    return InferenceClient(
        provider="hf-inference",
        api_key=hf_token
    )


gemini_client = create_gemini_client()
hf_client = create_huggingface_client()


# ==========================
# NLTK Setup
# ==========================

def setup_nltk():
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)


# ==========================
# Load Documents
# ==========================

def load_documents(folder=DATA_FOLDER):
    """
    Loads .txt files and splits them into sentences.
    We keep the original sentence text.
    Do NOT remove stopwords here, because the LLM needs natural context.
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Folder '{folder}' does not exist. Create it and put .txt files inside."
        )

    chunks = []

    for file_name in os.listdir(folder):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder, file_name)

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            sentences = sent_tokenize(text)

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    chunks.append(sentence)

    if not chunks:
        raise ValueError(
            f"No text found. Make sure '{folder}' contains .txt files with content."
        )

    print(f"Loaded {len(chunks)} text chunks.")
    return chunks


# ==========================
# Hugging Face Cloud Embeddings
# ==========================

def normalize_hf_embedding_output(output):
    """
    Hugging Face feature_extraction can return different shapes depending
    on the model/provider.

    We convert it into a clean 2D numpy array:
    shape = [number_of_texts, embedding_dimension]
    """
    arr = np.array(output, dtype="float32")

    # Case 1:
    # Single text embedding:
    # [dimension]
    if arr.ndim == 1:
        arr = np.expand_dims(arr, axis=0)

    # Case 2:
    # Token embeddings:
    # [tokens, dimension]
    # We mean-pool tokens into one sentence vector.
    elif arr.ndim == 2:
        # If this is already [batch, dim], keep it.
        # If this came from one text as [tokens, dim], this is ambiguous.
        # For a single input call, we treat it as token embeddings.
        pass

    # Case 3:
    # Batch token embeddings:
    # [batch, tokens, dimension]
    elif arr.ndim == 3:
        arr = arr.mean(axis=1)

    return arr.astype("float32")


def embed_texts_with_huggingface(texts, batch_size=BATCH_SIZE):
    """
    Creates embeddings using Hugging Face cloud inference.
    """
    all_embeddings = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        print(f"Embedding batch {start // batch_size + 1}...")

        result = hf_client.feature_extraction(
            batch,
            model=HF_EMBEDDING_MODEL
        )

        embeddings = normalize_hf_embedding_output(result)

        # Safety check:
        # Sometimes a provider may return token-level embeddings for each item.
        # If the batch returns 3D, it was already mean-pooled above.
        if embeddings.shape[0] != len(batch):
            fixed_embeddings = []

            for text in batch:
                single_result = hf_client.feature_extraction(
                    text,
                    model=HF_EMBEDDING_MODEL
                )

                single_embedding = np.array(single_result, dtype="float32")

                if single_embedding.ndim == 1:
                    pass
                elif single_embedding.ndim == 2:
                    single_embedding = single_embedding.mean(axis=0)
                elif single_embedding.ndim == 3:
                    single_embedding = single_embedding.mean(axis=1)[0]

                fixed_embeddings.append(single_embedding)

                time.sleep(0.1)

            embeddings = np.array(fixed_embeddings, dtype="float32")

        all_embeddings.append(embeddings)

    final_embeddings = np.vstack(all_embeddings).astype("float32")

    print(f"Created embeddings shape: {final_embeddings.shape}")

    return final_embeddings


def embed_query_with_huggingface(query):
    """
    Creates one query embedding using Hugging Face cloud inference.
    """
    result = hf_client.feature_extraction(
        query,
        model=HF_EMBEDDING_MODEL
    )

    embedding = np.array(result, dtype="float32")

    if embedding.ndim == 1:
        embedding = np.expand_dims(embedding, axis=0)

    elif embedding.ndim == 2:
        # Token embeddings -> mean pooling
        embedding = embedding.mean(axis=0, keepdims=True)

    elif embedding.ndim == 3:
        embedding = embedding.mean(axis=1)

    return embedding.astype("float32")


# ==========================
# FAISS
# ==========================

def create_faiss_index(embeddings):
    """
    Creates FAISS index from Hugging Face embeddings.
    """
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"FAISS index created with {index.ntotal} vectors.")
    return index


def retrieve(query, index, chunks, k=TOP_K):
    """
    Converts query to Hugging Face embedding, then searches FAISS.
    """
    query_embedding = embed_query_with_huggingface(query)

    distances, indexes = index.search(query_embedding, k)

    print("\nFAISS distances:", distances)
    print("FAISS indexes:", indexes)

    results = []

    for idx in indexes[0]:
        if idx != -1:
            results.append(chunks[idx])

    return results


# ==========================
# Gemini LLM
# ==========================

def ask_gemini(context, question):
    """
    Gemini is the LLM.
    Hugging Face is only used for embeddings.
    """
    prompt = f"""
You are a helpful RAG assistant.

Use the provided context to answer the user's question.

Rules:
1. First answer using only the provided context.
2. If the context does not contain enough information, say:
   "I do not have enough information in the documents, but based on general knowledge..."
3. Keep the answer simple and clear.
4. Do not invent document facts.

Context:
{context}

Question:
{question}

Answer:
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0
            )
        )
    )

    return response.text.strip()


# ==========================
# Main
# ==========================

def main():
    setup_nltk()

    print("Loading documents...")
    chunks = load_documents(DATA_FOLDER)

    print("\nCreating Hugging Face cloud embeddings...")
    document_embeddings = embed_texts_with_huggingface(chunks)

    print("\nCreating FAISS index...")
    index = create_faiss_index(document_embeddings)

    print("\nRAG system is ready.")
    print("Embedding model: Hugging Face cloud")
    print("Vector DB: FAISS local")
    print("LLM: Gemini cloud")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nAsk something: ").strip()

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            print("Please enter a real question.")
            continue

        top_chunks = retrieve(
            query=question,
            index=index,
            chunks=chunks,
            k=TOP_K
        )

        context = "\n".join(top_chunks)

        print("\nRetrieved Context:")
        print(context)

        answer = ask_gemini(context, question)

        print("\nGemini Answer:")
        print(answer)


if __name__ == "__main__":
    main()