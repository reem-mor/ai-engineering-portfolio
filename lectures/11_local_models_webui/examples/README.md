# Example I/O — Lecture 11

Recorded **input/output** pairs from local model runs on Intel Arc 140V (Vulkan, `n_gpu_layers=999`).

| File | Stack | Topic |
|------|-------|--------|
| [`qwen25_factual.json`](io/qwen25_factual.json) | llama-cpp-python | Qwen 2.5 — simple Q&A |
| [`qwen25_reasoning.json`](io/qwen25_reasoning.json) | llama-cpp-python | Qwen 2.5 — inline step-by-step |
| [`qwen3_fast_no_think.json`](io/qwen3_fast_no_think.json) | llama-cpp-python | Qwen 3 — `/no_think` fast mode |
| [`qwen3_reasoning_thinking.json`](io/qwen3_reasoning_thinking.json) | llama-cpp-python | Qwen 3 — hybrid thinking |
| [`huggingface_download.json`](io/huggingface_download.json) | Hugging Face Hub | Model download |
| [`llama_server_api.json`](io/llama_server_api.json) | llama-server | OpenAI-compatible API |
| [`ragas_eval_sample.json`](io/ragas_eval_sample.json) | RAGAS | RAG evaluation dataset |
| [`rag_rerank_sample.json`](io/rag_rerank_sample.json) | Local RAG + rerank | Retrieve, rerank, generate |

Run the matching demo under [`../demos/`](../demos/) or [`../main.py`](../main.py) to reproduce live output.
