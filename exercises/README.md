# Exercises Index

Runnable exercises and demos live next to their lectures to keep imports and paths stable. Use this page as a table of contents.

Full lecture list: [`lectures/README.md`](../lectures/README.md) · Homework: [`homework/README.md`](../homework/README.md).

## NLP and RAG (Lecture 04)

| Path | Description |
|------|-------------|
| [`lectures/04_nlp_rag/exercises/`](../lectures/04_nlp_rag/exercises/) | Tokenization and word-vector exercises |
| [`lectures/04_nlp_rag/demos/`](../lectures/04_nlp_rag/demos/) | NLP demos: FAISS, embeddings, RAG example scripts |
| [`lectures/04_nlp_rag/data/`](../lectures/04_nlp_rag/data/) | Sample corpus for demos |

## Flask (Lecture 05)

| Path | Description |
|------|-------------|
| [`lectures/05_flask_intro/`](../lectures/05_flask_intro/) | Flask routes, templates, static files, Dockerfile |

Run: `python app.py` from that folder.

## Flask + RAG + SQLite (Lecture 06)

| Path | Description |
|------|-------------|
| [`lectures/06_flask_advanced_rag/`](../lectures/06_flask_advanced_rag/) | Full RAG web prototype with SQLite history |

Run: copy `.env.example` to `.env`, then `python app.py`.

## Docker and AWS (Lecture 07)

| Path | Description |
|------|-------------|
| [`lectures/07_docker_aws/`](../lectures/07_docker_aws/) | AWS architecture notes and Mermaid diagram |

## MCP (Lecture 08)

| Path | Description |
|------|-------------|
| [`lectures/08_mcp/`](../lectures/08_mcp/) | Stdio MCP server, Cursor `mcp.json` setup, Gemini tool-calling contrast |
| [`lectures/08_mcp/server/tools_server.py`](../lectures/08_mcp/server/tools_server.py) | FastMCP server (`get_weather`, `get_joke`) |
| [`lectures/08_mcp/demos/tool_calling_demo.py`](../lectures/08_mcp/demos/tool_calling_demo.py) | Ad-hoc JSON tool-calling without MCP |

Setup: `pip install -r requirements.txt`, copy `config/mcp.json.example` to `.cursor/mcp.json` at repo root.

Run tests: `python -m pytest tests -q` from `lectures/08_mcp`.

Run tests: `python -m pytest tests -q` from `lectures/08_mcp`.

## Bedrock Flows & n8n (Lecture 09)

| Path | Description |
|------|-------------|
| [`lectures/09_flows_bedrock_n8n/`](../lectures/09_flows_bedrock_n8n/) | Bedrock Flows + n8n workflow exports |
| [`homework/hw06/`](../homework/hw06/) | Customer-support agent homework |

## LangChain & LangGraph (Lecture 10)

| Path | Description |
|------|-------------|
| [`lectures/10_langchain_langgraph/`](../lectures/10_langchain_langgraph/) | LangChain/LangGraph RAG exercises, ML demos |
| Run tests | `pip install -r requirements.txt && pytest -q` |

## Local models & Open WebUI (Lecture 11)

| Path | Description |
|------|-------------|
| [`lectures/11_local_models_webui/`](../lectures/11_local_models_webui/) | Ollama, Open WebUI, KB concepts |
| [`homework/hw07/`](../homework/hw07/) | Open WebUI + MCP-style tools server |

## Homework labs

| Path | Description |
|------|-------------|
| [`homework/hw03/`](../homework/hw03/) | Titanic ticket CLI — includes pytest |
| [`homework/hw05/nginx-docker-lab/`](../homework/hw05/nginx-docker-lab/) | EC2, Docker, Nginx hands-on lab |
| [`homework/hw06/n8n-customer-support-agent/`](../homework/hw06/n8n-customer-support-agent/) | n8n agent workflow |
| [`homework/hw07/open-webui-tools/`](../homework/hw07/open-webui-tools/) | FastAPI tools server for Open WebUI |

## Related documentation

- Setup: [`docs/setup.md`](../docs/setup.md)
- RAG notes: [`docs/rag-notes.md`](../docs/rag-notes.md)
- Docker/AWS: [`docs/docker-aws-notes.md`](../docs/docker-aws-notes.md)
