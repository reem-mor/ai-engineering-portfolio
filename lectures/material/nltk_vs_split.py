from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt', quiet=True)

text = "Don't stop believing, hold on to that feeling"

print("split():", text.split())
print("word_tokenize():", word_tokenize(text))