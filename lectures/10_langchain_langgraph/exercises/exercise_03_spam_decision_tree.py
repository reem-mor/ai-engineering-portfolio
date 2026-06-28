"""Exercise 03: Spam decision tree on toy email features."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.spam_tree_model import predict_spam, train_spam_tree


def main() -> None:
    result = train_spam_tree()

    print("=== Decision tree rules ===")
    print(result.rules_text.rstrip())
    print(
        "\nTraining accuracy on tiny table (demo only): "
        f"{result.training_accuracy:.3f}"
    )
    print("Note: one contradictory row limits accuracy to 0.90 on this table.")

    print("\n=== Sample predictions ===")
    samples = [(1, 0), (0, 0), (0, 1)]
    for contains_free, many_exclamations in samples:
        label, leaf_vote = predict_spam(
            result.classifier,
            contains_free,
            many_exclamations,
        )
        print(
            f"contains_free={contains_free}, many_exclamations={many_exclamations} "
            f"-> leaf_vote={leaf_vote:.3f}, predicted={label}"
        )


if __name__ == "__main__":
    main()
