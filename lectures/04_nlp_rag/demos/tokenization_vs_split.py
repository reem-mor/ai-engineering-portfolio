"""Demo: why word_tokenize is better than str.split() for NLP."""
import nltk

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import word_tokenize

text = "Don't stop believing! It's amazing."

print("Input          :", text)
print("split()        :", text.split())
print("word_tokenize():", word_tokenize(text))
# split()        → ["Don't", 'stop', 'believing!', "It's", 'amazing.']
# word_tokenize()→ ['Do', "n't", 'stop', 'believing', '!', 'It', "'s", 'amazing', '.']
