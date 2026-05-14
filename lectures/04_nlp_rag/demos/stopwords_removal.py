"""Demo: remove English stopwords after tokenization."""
import nltk

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

STOPS = set(stopwords.words('english'))

text = "This is an example showing how tokenization and stopword removal work."
tokens = [t.lower() for t in word_tokenize(text)]
filtered = [t for t in tokens if t.isalpha() and t not in STOPS]

print("Original tokens:", tokens)
print("Filtered tokens:", filtered)
