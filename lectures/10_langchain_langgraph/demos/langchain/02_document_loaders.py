"""LangChain demo: loading documents with TextLoader."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_community.document_loaders import TextLoader

from lecture_config import DATA_DIR

report_path = DATA_DIR / "risk_analysis_report.txt"
loader = TextLoader(str(report_path), encoding="utf-8")
docs = loader.load()

print(f"Loaded {len(docs)} document(s) from {report_path.name}")
for doc in docs[:1]:
    print("----")
    print(doc.page_content[:300], "...")
