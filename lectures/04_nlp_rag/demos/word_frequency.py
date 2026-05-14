"""Demo: word frequency analysis with Counter."""
import nltk
from collections import Counter

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import word_tokenize

text = "Python is great. Python is simple. NLP with Python is powerful!"
tokens = [t.lower() for t in word_tokenize(text) if t.isalpha()]
freq = Counter(tokens)

print("Tokens:", tokens)
print("\nWord frequencies:")
for word, count in freq.most_common():
    print(f"  {word:<15} {count}")
