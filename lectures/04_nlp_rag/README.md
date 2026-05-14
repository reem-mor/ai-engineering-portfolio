# Lecture 04 — NLP & RAG Pipeline

---

## Topics Covered

- Tokenization: `word_tokenize`, `sent_tokenize` (NLTK)
- Stopword removal
- Stemming (`PorterStemmer`) vs Lemmatization (`WordNetLemmatizer`)
- POS tagging and WordNet POS mapping
- Naive lexicon-based sentiment analysis
- Word frequency with `Counter`
- Dense word embeddings: Word2Vec / GloVe (gensim)
- Hugging Face cloud embeddings (IBM Granite via `InferenceClient`)
- FAISS vector index: `IndexFlatIP`, L2 normalisation for cosine similarity
- RAG (Retrieval-Augmented Generation) pipeline end-to-end
- Gemini LLM integration via `google-genai`

---

## Key Concepts You Must Know

### Why Tokenize?
Raw text is a string. NLP models need structured units. Tokenization is always the first step.

```
"Don't stop!" → ["Do", "n't", "stop", "!"]    # word_tokenize
"A. B. C."    → ["A.", "B.", "C."]             # sent_tokenize
text.split()  → ["Don't", "stop!"]             # naive — misses punctuation
```

`word_tokenize` handles contractions and punctuation correctly; `.split()` does not.

### Stopwords
High-frequency words that add no semantic signal: *the, is, at, which, on...*
Remove them to reduce noise before vectorisation or frequency analysis.

```python
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))
filtered = [t for t in tokens if t.lower() not in stops and t.isalpha()]
```

### Stemming vs Lemmatization

| | Stemming | Lemmatization |
|---|---|---|
| Technique | Chop suffix by rule | Look up word in dictionary |
| Output | Not always a real word | Always a real word |
| Speed | Fast | Slower (needs WordNet) |
| Example | "running" → "run" | "better" → "good" |

Lemmatization requires the POS tag for accuracy: `lemmatize("better", pos=wordnet.ADJ)`.

### Word Embeddings
Words are mapped to dense vectors where **similar words are close** in vector space.

- **Word2Vec** (Google, 2013): trained on local context windows.
- **GloVe** (Stanford, 2014): trained on global co-occurrence statistics.
- Gensim's `api.load("glove-wiki-gigaword-50")` downloads a 50-dim pretrained model.

Vector arithmetic: `king − man + woman ≈ queen` — semantics are encoded in directions.

### Hugging Face Embeddings (Cloud)
For production-quality embeddings, use a cloud model:
```python
from huggingface_hub import InferenceClient
client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)
result = client.feature_extraction(texts, model="ibm-granite/granite-embedding-97m-multilingual-r2")
# result shape: [batch_size, embedding_dim]
```

### FAISS Vector Index
FAISS (Facebook AI Similarity Search) enables sub-second similarity search over millions of vectors.

```
IndexFlatIP   → exact inner product (= cosine similarity when vectors are L2-normalised)
IndexIVFFlat  → approximate, faster for large datasets (>1M vectors)
```

Workflow:
1. `faiss.normalize_L2(embeddings)` — normalise document vectors
2. `index = faiss.IndexFlatIP(dim)` — create index
3. `index.add(embeddings)` — add all vectors
4. `faiss.normalize_L2(query_vec)` — normalise query too
5. `scores, indices = index.search(query_vec, k=3)` — retrieve top-k

### RAG Architecture

```
User Question
     │
     ▼
[Embed question]  ←  HuggingFace InferenceClient
     │
     ▼
[FAISS search]  →  top-k text chunks
     │
     ▼
[Build prompt]  =  system_rules + retrieved_context + question
     │
     ▼
[Gemini LLM]  →  Answer
```

Two models, two different jobs:
- **Embedding model** (HF): converts text → vector. Lightweight, fast, run in batch.
- **LLM** (Gemini): reads context + question → natural language answer. Heavy, run per query.

RAG is preferable to fine-tuning when:
- The knowledge base changes frequently.
- You need source attribution.
- You have limited compute for fine-tuning.

---

## Exercises

### Exercise 1 — Tokenization & Overlap (`exercises/exercise_01_tokenization.py`)
Two sentences are given. Your task:
1. Tokenize both: lowercase, alpha-only tokens using `word_tokenize`.
2. Count how many words they share.
3. Compute the Jaccard overlap percentage: `|A ∩ B| / |A ∪ B| * 100`.

Run the file — expected output:
```
Tokens A: ['natural', 'language', 'processing', 'is', 'fun']
Tokens B: ['i', 'find', 'processing', 'natural', 'language', 'quite', 'enjoyable']
Shared count: 3
Overlap %: 37.5%
```

### Exercise 2 — Word Vector Analogies (`exercises/exercise_02_word_vectors.py`)
Using GloVe 50-dim embeddings:
1. Print the cosine similarity between "king" and "queen".
2. Solve the analogy: `paris + germany − france = ?` (print top-10 candidates).

*Note: First run downloads ~66 MB of embeddings — be patient.*

### Exercise 3 — Build a Mini RAG (`demos/rag_example.py`)
1. Set `GEMINI_API_KEY` and `HF_TOKEN` as environment variables.
2. Place a `.txt` file in `data/` (or use the provided `risk_analysis_report.txt`).
3. Run the script — it will embed, index, then start an interactive Q&A loop.
4. Try: *"What are the top risks identified?"* and *"Who is responsible for R-02?"*

---

## Demo Files

| File | What it shows |
|------|--------------|
| `demos/nltk_basic.py` | `word_tokenize` on a single sentence |
| `demos/tokenization_vs_split.py` | How `split()` differs from `word_tokenize` for contractions |
| `demos/stopwords_removal.py` | Filter stopwords from token list |
| `demos/lemmatization.py` | Stemming vs lemmatization side-by-side, POS-aware |
| `demos/sentiment.py` | Lexicon-based positive/negative scoring |
| `demos/word_frequency.py` | `Counter` on tokenized text |
| `demos/word2vec.py` | GloVe similarity and vector analogies |
| `demos/gemini_example.py` | Single Gemini API call |
| `demos/rag_example.py` | Full CLI RAG pipeline |

---

## Setup

```bash
# NLTK data (run once)
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger_eng')"

# API keys (set before running demos)
export GEMINI_API_KEY="your-key"
export HF_TOKEN="your-token"
```
