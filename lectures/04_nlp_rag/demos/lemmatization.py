"""Demo: stemming vs POS-aware lemmatization."""
import nltk

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

from nltk import word_tokenize, pos_tag
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet


def get_wordnet_pos(treebank_tag: str) -> str:
    """Map a Penn Treebank POS tag to a WordNet POS constant."""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    if treebank_tag.startswith('N'):
        return wordnet.NOUN
    if treebank_tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN  # fallback


text = "The striped bats are hanging on their feet and they are better than before."
tokens = word_tokenize(text)
pos_tags = pos_tag(tokens)

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

print(f"{'Token':<12} {'Stemmed':<12} {'Lemmatized'}")
print("-" * 36)
for token, pos in pos_tags:
    stem = stemmer.stem(token)
    lemma = lemmatizer.lemmatize(token, get_wordnet_pos(pos))
    print(f"{token:<12} {stem:<12} {lemma}")
