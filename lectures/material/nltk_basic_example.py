import nltk

#download the new tokenizer models

nltk.download('punkt_tab')

from nltk.tokenize import word_tokenize

text = "natural language processing with python is fun"
tokens = word_tokenize(text)
print(tokens)
