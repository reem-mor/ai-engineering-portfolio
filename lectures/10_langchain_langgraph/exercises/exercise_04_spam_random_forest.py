"""Exercise 04: Spam random forest on toy email features."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.spam_forest_model import predict_spam, train_spam_forest


def main() -> None:
    result = train_spam_forest()

    print("=== Random forest (tiny spam table) ===")
    print(
        "Training accuracy on tiny table (demo only): "
        f"{result.training_accuracy:.3f}"
    )
    print(
        "Feature importances "
        f"[{', '.join(result.feature_names)}]: "
        f"{np.round(result.feature_importances, 3)}"
    )

    print("\n=== Sample predictions ===")
    samples = [(1, 1), (1, 0), (0, 1), (0, 0)]
    for contains_free, many_exclamations in samples:
        label, spam_score = predict_spam(
            result.classifier,
            contains_free,
            many_exclamations,
        )
        print(
            f"contains_free={contains_free}, many_exclamations={many_exclamations} "
            f"-> spam_score={spam_score:.3f}, predicted={label}"
        )


if __name__ == "__main__":
    main()
