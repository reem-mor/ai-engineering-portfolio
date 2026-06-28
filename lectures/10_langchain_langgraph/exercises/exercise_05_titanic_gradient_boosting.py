"""Exercise 05: Titanic survival prediction with gradient boosting libraries."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.titanic_boosting_model import (
    EXAMPLE_FEATURES,
    load_titanic_features,
    train_all_boosters,
)


def main() -> None:
    data = load_titanic_features()

    print("Feature sample (first 8 rows):")
    print(data.feature_frame.head(8).to_string(index=False))

    results = train_all_boosters(data)
    example_label = (
        f"is_female={EXAMPLE_FEATURES[0]},"
        f"is_child={EXAMPLE_FEATURES[1]},"
        f"is_first_class={EXAMPLE_FEATURES[2]}"
    )

    for result in results:
        print(f"\n=== {result.name} ===")
        print(f"Accuracy: {result.accuracy:.3f}")
        print(f"Feature importances: {result.feature_importances}")
        print(f"Example prob ({example_label}): {result.example_prob:.3f}")


if __name__ == "__main__":
    main()
