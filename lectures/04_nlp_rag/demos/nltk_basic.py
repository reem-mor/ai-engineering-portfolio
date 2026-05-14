"""Demo: basic NLTK word tokenization."""
import nltk

nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import word_tokenize

text = "Natural Language Processing with Python is fun!"
tokens = word_tokenize(text)
print("Input :", text)
print("Tokens:", tokens)
