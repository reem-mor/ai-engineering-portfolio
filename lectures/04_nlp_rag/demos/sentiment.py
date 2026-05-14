"""Demo: lexicon-based sentiment analysis."""
import nltk

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import word_tokenize

POSITIVE = {"good", "great", "happy", "fun", "love", "powerful", "excellent", "amazing"}
NEGATIVE = {"bad", "sad", "hate", "terrible", "hard", "awful", "boring", "poor"}


def sentiment(text: str) -> str:
    tokens = [t.lower() for t in word_tokenize(text)]
    pos = sum(1 for t in tokens if t in POSITIVE)
    neg = sum(1 for t in tokens if t in NEGATIVE)
    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    return "Neutral"


if __name__ == "__main__":
    examples = [
        "I love using Python for NLP. It's fun and powerful!",
        "This is a terrible example, I hate bugs.",
        "The weather is okay today.",
    ]
    for text in examples:
        print(f"{sentiment(text):10}  {text!r}")
