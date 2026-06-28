"""Offline tests for the Iris K-means exercise."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.iris_kmeans_model import (
    FEATURE_NAMES,
    SPECIES_BY_PETAL_ORDER,
    cluster_iris,
    mapped_cluster_accuracy,
    plot_clusters,
    summarize_dataset,
)


def test_dataset_shape_and_features() -> None:
    summary = summarize_dataset()
    assert summary.feature_names == FEATURE_NAMES
    assert summary.n_samples == 150
    assert summary.n_features == 4
    assert len(summary.target_names) == 3
    assert sum(summary.class_counts.values()) == summary.n_samples


def test_three_clusters() -> None:
    result = cluster_iris()
    assert len(set(result.cluster_labels)) == 3


def test_centroid_species_order() -> None:
    result = cluster_iris()
    ordered = sorted(
        result.centroid_species.items(),
        key=lambda item: result.centers[item[0], 1],
    )
    assigned_species = [species for _, species in ordered]
    assert assigned_species == list(SPECIES_BY_PETAL_ORDER)


def test_clustering_matches_iris_well() -> None:
    result = cluster_iris()
    # Two-feature K-means; ~88% mapped accuracy is expected on Iris.
    assert mapped_cluster_accuracy(result) >= 0.85


def test_plot_returns_figure_without_display() -> None:
    result = cluster_iris()
    fig = plot_clusters(result, show=False)
    assert fig is not None
    import matplotlib.pyplot as plt

    plt.close(fig)
