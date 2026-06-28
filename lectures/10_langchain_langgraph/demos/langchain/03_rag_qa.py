"""LangChain demo: RAG Q&A over a text document with FAISS."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_classic.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from lecture_config import DATA_DIR, require_openai_api_key


def main() -> None:
    api_key = require_openai_api_key()

    loader = TextLoader(str(DATA_DIR / "risk_analysis_report.txt"), encoding="utf-8")
    docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = FAISS.from_documents(splits, embeddings)

    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(api_key=api_key),
        retriever=vectorstore.as_retriever(),
    )

    query = "What is the date of risk analysis report?"
    print(qa.run(query))


if __name__ == "__main__":
    main()
