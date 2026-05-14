"""
Word vector analogies with GloVe embeddings.

First run downloads ~66 MB of GloVe data to ~/.cache/gensim-data/.
Requires: pip install gensim
"""
import gensim.downloader as api


def main() -> None:
    print("Loading GloVe 50-dim model (one-time download ~66 MB)...")
    model = api.load("glove-wiki-gigaword-50")

    # Similarity
    sim = model.similarity("king", "queen")
    print(f"\nSimilarity  king ~ queen: {sim:.4f}")

    # Vector analogy: paris + germany - france = ?
    candidates = [w for w, _ in model.most_similar(
        positive=["paris", "germany"],
        negative=["france"],
        topn=10,
    )]
    print(f"\nAnalogy  paris + germany − france → top-10: {candidates}")


if __name__ == "__main__":
    main()
