"""Exercise 01: Wisconsin breast cancer classifier using mean radius and mean texture."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.breast_cancer_model import (
    predict_diagnosis,
    summarize_dataset,
    train_classifier,
)


def _prompt_float(prompt: str) -> float | None:
    raw = input(prompt).strip()
    if not raw or raw.lower() in {"q", "quit", "exit"}:
        return None
    return float(raw)


def main() -> None:
    summary = summarize_dataset()
    print("=== Dataset investigation ===")
    print(f"Samples: {summary.n_samples}")
    print(f"Features used: {', '.join(summary.feature_names)}")
    print(f"All feature count in dataset: {summary.n_features}")
    print(f"Target classes: {', '.join(summary.target_names)}")
    print(
        f"Class balance - malignant: {summary.malignant_count}, "
        f"benign: {summary.benign_count}"
    )

    result = train_classifier()
    print("\n=== Supervised training ===")
    print(f"Test accuracy: {result.test_accuracy:.3f}")
    print(result.report)

    print("\n=== Interactive prediction ===")
    print("Enter mean radius and mean texture (or press Enter to quit).")
    while True:
        mean_radius = _prompt_float("Mean radius: ")
        if mean_radius is None:
            break
        mean_texture = _prompt_float("Mean texture: ")
        if mean_texture is None:
            break

        label, confidence = predict_diagnosis(
            result.pipeline,
            result.target_names,
            mean_radius,
            mean_texture,
        )
        print(f"Predicted diagnosis: {label} (confidence={confidence:.2f})\n")


if __name__ == "__main__":
    main()
