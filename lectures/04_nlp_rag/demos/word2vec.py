"""Demo: GloVe word embeddings — similarity and vector analogies.

First run downloads ~66 MB to ~/.cache/gensim-data/.
Requires: pip install gensim
"""
import gensim.downloader as api


def main() -> None:
    print("Loading GloVe 50-dim embeddings (one-time download ~66 MB)...")
    model = api.load("glove-wiki-gigaword-50")

    print(f"\nSimilarity  king ~ queen  : {model.similarity('king', 'queen'):.4f}")
    print(f"Similarity  cat  ~ dog    : {model.similarity('cat', 'dog'):.4f}")
    print(f"Similarity  car  ~ banana : {model.similarity('car', 'banana'):.4f}")

    print("\nAnalogy  paris + germany − france → top-10:")
    result = [w for w, _ in model.most_similar(
        positive=["paris", "germany"],
        negative=["france"],
        topn=10,
    )]
    print(" ", result)


if __name__ == "__main__":
    main()
