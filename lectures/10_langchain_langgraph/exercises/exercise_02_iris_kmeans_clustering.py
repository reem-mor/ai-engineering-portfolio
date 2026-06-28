"""Exercise 02: Iris K-means clustering on sepal length and petal length."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.iris_kmeans_model import (
    cluster_iris,
    mapped_cluster_accuracy,
    plot_clusters,
    summarize_dataset,
)


def main() -> None:
    summary = summarize_dataset()
    print("=== Dataset investigation ===")
    print(f"Samples: {summary.n_samples}")
    print(f"Features used: {', '.join(summary.feature_names)}")
    print(f"All feature count in dataset: {summary.n_features}")
    print(f"Target classes: {', '.join(summary.target_names)}")
    for name, count in summary.class_counts.items():
        print(f"  {name}: {count}")

    result = cluster_iris()
    accuracy = mapped_cluster_accuracy(result)

    print("\n=== K-Means clustering (k=3) ===")
    order = sorted(
        result.centroid_species.items(),
        key=lambda item: result.centers[item[0], 1],
    )
    for cluster_id, species in order:
        sepal, petal = result.centers[cluster_id]
        print(
            f"Centroid {cluster_id} -> {species} "
            f"(sepal={sepal:.2f}, petal={petal:.2f})"
        )
    print(f"Mapped cluster accuracy vs ground truth: {accuracy:.3f}")

    plot_clusters(result)


if __name__ == "__main__":
    main()
