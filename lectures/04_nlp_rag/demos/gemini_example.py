"""Demo: single Gemini API call.

Set environment variable before running:
    export GEMINI_API_KEY="your-key"
"""
import os
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain what a RAG pipeline is in two sentences.",
)

print(response.text)
