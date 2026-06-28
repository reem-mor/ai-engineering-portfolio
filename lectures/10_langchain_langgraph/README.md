# Lecture 10 — LangChain & LangGraph

---

## Overview

This lecture connects **classical ML decision-making** (supervised, unsupervised, decision trees, gradient boosting) and **deep learning** (PyTorch transfer learning) with **LangChain** (memory, document loading, RAG) and **LangGraph** (stateful routing graphs).

You will:

1. Train and evaluate small scikit-learn models (offline).
2. Run a pretrained PyTorch MobileNetV3 classifier on a sample image (offline; downloads ImageNet weights on first run).
3. Build LangChain pipelines for chat memory, document loading, and RAG Q&A.
4. Route support tickets with a LangGraph `StateGraph`.
5. Combine sklearn intent classification with LangChain RAG in one support assistant.
6. Complete **Exercise 01**: breast cancer diagnosis predictor (pure sklearn, interactive CLI).
7. Complete **Exercise 02**: Iris K-means clustering (pure sklearn, scatter plot).
8. Complete **Exercise 03**: spam decision tree (pure sklearn, rule export).
9. Complete **Exercise 04**: spam random forest (pure sklearn, feature importances).
10. Complete **Exercise 05**: Titanic gradient boosting (XGBoost, LightGBM, CatBoost on shared hw03 dataset).

---

## Topics Covered

- Supervised learning: logistic regression
- Unsupervised learning: KMeans clustering
- Decision trees: loan approval visualization
- LangChain: `ConversationChain`, document loaders, FAISS + `RetrievalQA`
- LangGraph: `StateGraph`, conditional edges, typed state
- Hybrid pattern: sklearn classifier + RAG + LLM triage chain
- Wisconsin breast cancer dataset: feature selection, train/test split, CLI prediction
- Iris dataset: two-feature K-means, centroid labeling by petal length, visualization
- Toy spam tables: decision tree rules and random forest voting
- Titanic survival: binary features + gradient boosting (XGBoost, LightGBM, CatBoost)
- PyTorch: pretrained MobileNetV3, ImageNet top-k inference, CPU/GPU device selection

---

## Prerequisites

- Python 3.12+
- `OPENAI_API_KEY` for LangChain/LangGraph demos only (ML demos and exercise run offline)

---

## Setup

### 1. Virtual environment and dependencies

```powershell
cd lectures\10_langchain_langgraph
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment variables (OpenAI demos only)

```powershell
copy .env.example .env
# Edit .env with your OPENAI_API_KEY
```

ML demos (`demos/ml/01`–`05`) and exercises 01–05 do **not** require an API key.

---

## Run

### Part 1 — ML foundations (offline)

```powershell
python demos\ml\01_supervised_spam.py
python demos\ml\02_unsupervised_kmeans.py
python demos\ml\03_decision_tree_loan.py
python demos\ml\05_pytorch_mobilenet.py
```

The PyTorch demo loads pretrained **MobileNetV3-Small** (ImageNet), reads `data/sample.jpg` (or a path you pass on the command line), and prints top-5 label probabilities as JSON. First run downloads model weights (~10 MB).

```powershell
python demos\ml\05_pytorch_mobilenet.py
python demos\ml\05_pytorch_mobilenet.py path\to\your\img.png
```

### Part 2 — LangChain (requires `OPENAI_API_KEY`)

```powershell
python demos\langchain\01_memory_chat.py
python demos\langchain\02_document_loaders.py
python demos\langchain\03_rag_qa.py
```

### Part 3 — LangGraph (requires `OPENAI_API_KEY`)

```powershell
python demos\langgraph\01_support_router.py
python demos\langgraph\02_loan_decision_chains.py
```

See flow diagrams in [`docs/support_router_flow.txt`](docs/support_router_flow.txt) and [`docs/loan_decision_flow.txt`](docs/loan_decision_flow.txt).

### Part 4 — Integration (requires `OPENAI_API_KEY`)

```powershell
python demos\ml\04_sklearn_langchain_combo.py
```

### Exercise 01 — Breast cancer predictor (offline)

```powershell
python exercises\exercise_01_breast_cancer_predictor.py
```

The script will:

1. Load `sklearn.datasets.load_breast_cancer`
2. Investigate dataset shape and class balance
3. Train on **mean radius** and **mean texture** only
4. Prompt you for feature values and print the predicted diagnosis (`malignant` / `benign`)

Example interaction:

```
Mean radius: 17.99
Mean texture: 10.38
Predicted diagnosis: malignant (confidence=0.91)
```

Press Enter on an empty prompt to quit.

### Exercise 02 — Iris K-means clustering (offline)

```powershell
python exercises\exercise_02_iris_kmeans_clustering.py
```

The script will:

1. Load `sklearn.datasets.load_iris`
2. Investigate dataset shape and class balance (150 samples, 50 per species)
3. Cluster on **sepal length (cm)** and **petal length (cm)** only (`k=3`)
4. Label centroids by ascending petal length: setosa → versicolor → virginica
5. Show a scatter plot of clusters and centroids

No API key required.

### Exercise 03 — Spam decision tree (offline)

```powershell
python exercises\exercise_03_spam_decision_tree.py
```

The script will:

1. Train a shallow decision tree on a 10-row spam feature table
2. Print human-readable rules (`contains_free`, `many_exclamations`)
3. Show sample predictions with **leaf vote share** (not calibrated probability)
4. Report training accuracy on the tiny table (demo only; one contradictory row)

### Exercise 04 — Spam random forest (offline)

```powershell
python exercises\exercise_04_spam_random_forest.py
```

The script will:

1. Train a small random forest on a 10-row spam feature table
2. Print training accuracy (demo only) and feature importances
3. Show sample predictions with threshold-based spam score

No API key required.

### Exercise 05 — Titanic gradient boosting (offline)

```powershell
python exercises\exercise_05_titanic_gradient_boosting.py
```

The script will:

1. Load the shared Titanic dataset from `homework/hw03/data/titanic.csv`
2. Build three binary features: `is_female`, `is_child`, `is_first_class`
3. Train XGBoost, LightGBM, and CatBoost with a stratified train/validation split
4. Print validation accuracy, feature importances, and an example survival probability

No API key required.

### Unit tests (offline)

```powershell
python -m pytest tests -q
```

---

## Verification checklist

1. Virtual environment exists and `pip install -r requirements.txt` succeeds.
2. `python demos\ml\01_supervised_spam.py` prints spam probability and accuracy.
3. `python demos\ml\05_pytorch_mobilenet.py` prints top-k ImageNet predictions.
4. `python demos\langchain\02_document_loaders.py` loads `data/risk_analysis_report.txt`.
5. `python exercises\exercise_05_titanic_gradient_boosting.py` prints three booster results.
6. `python -m pytest tests -q` passes.
7. No secrets committed (`git status` should not include `.env`).

---

## File layout

| Path | Purpose |
|------|---------|
| `lecture_config.py` | Shared paths (including Titanic CSV) and `OPENAI_API_KEY` loading |
| `demos/ml/` | scikit-learn demos (01–03), PyTorch MobileNet (05), sklearn+LangChain combo (04) |
| `demos/langchain/` | Memory chat, document loaders, RAG Q&A |
| `demos/langgraph/` | Support router graph, loan decision chains |
| `exercises/exercise_01_breast_cancer_predictor.py` | Interactive breast cancer classifier |
| `exercises/breast_cancer_model.py` | Train/predict helpers (used by tests) |
| `exercises/exercise_02_iris_kmeans_clustering.py` | Iris K-means clustering + plot |
| `exercises/iris_kmeans_model.py` | Cluster/label/plot helpers (used by tests) |
| `exercises/exercise_03_spam_decision_tree.py` | Spam decision tree rules + samples |
| `exercises/spam_tree_model.py` | Decision tree train/predict helpers |
| `exercises/exercise_04_spam_random_forest.py` | Spam random forest + importances |
| `exercises/spam_forest_model.py` | Random forest train/predict helpers |
| `exercises/spam_email_data.py` | Shared toy spam feature tables |
| `exercises/exercise_05_titanic_gradient_boosting.py` | Titanic gradient boosting comparison |
| `exercises/titanic_boosting_model.py` | Titanic load/train helpers (used by tests) |
| `exercises/mobilenet_model.py` | MobileNetV3 load/predict helpers (used by tests) |
| `tests/test_breast_cancer_exercise.py` | Offline pytest for exercise logic |
| `tests/test_iris_kmeans_exercise.py` | Offline pytest for Iris K-means exercise |
| `tests/test_spam_tree_exercise.py` | Offline pytest for spam decision tree |
| `tests/test_spam_forest_exercise.py` | Offline pytest for spam random forest |
| `tests/test_titanic_boosting_exercise.py` | Offline pytest for Titanic gradient boosting |
| `tests/test_mobilenet_demo.py` | Offline pytest for PyTorch MobileNet demo |
| `data/risk_analysis_report.txt` | Sample document for RAG demos |
| `data/sample.jpg` | Sample image for MobileNet classification demo |
| `docs/` | ASCII flow diagrams |
| `.env.example` | `OPENAI_API_KEY` template |

---

## Related documentation

- Lecture 04 RAG pipeline: [`lectures/04_nlp_rag/README.md`](../04_nlp_rag/README.md)
- LangGraph docs: https://langchain-ai.github.io/langgraph/
