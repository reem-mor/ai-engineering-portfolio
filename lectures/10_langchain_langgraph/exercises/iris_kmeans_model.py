"""Iris K-means clustering helpers for exercise 02 and tests."""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score

FEATURE_NAMES = ("sepal length (cm)", "petal length (cm)")
SPECIES_BY_PETAL_ORDER = ("setosa", "versicolor", "virginica")


@dataclass(frozen=True)
class DatasetSummary:
    n_samples: int
    n_features: int
    feature_names: tuple[str, ...]
    target_names: tuple[str, ...]
    class_counts: dict[str, int]


@dataclass(frozen=True)
class ClusteringResult:
    kmeans: KMeans
    cluster_labels: np.ndarray
    centroid_species: dict[int, str]
    feature_names: tuple[str, ...]
    centers: np.ndarray
    ground_truth: np.ndarray
    target_names: tuple[str, ...]


def load_two_feature_dataset() -> tuple[np.ndarray, np.ndarray, tuple[str, ...], tuple[str, ...]]:
    data = load_iris()
    feature_indices = [list(data.feature_names).index(name) for name in FEATURE_NAMES]
    X = data.data[:, feature_indices]
    y = data.target
    return X, y, FEATURE_NAMES, tuple(data.target_names)


def summarize_dataset() -> DatasetSummary:
    X, y, feature_names, target_names = load_two_feature_dataset()
    data = load_iris()
    class_counts = {
        name: int(np.sum(y == idx)) for idx, name in enumerate(target_names)
    }
    return DatasetSummary(
        n_samples=X.shape[0],
        n_features=len(data.feature_names),
        feature_names=feature_names,
        target_names=target_names,
        class_counts=class_counts,
    )


def _label_centroids_by_petal_length(centers: np.ndarray) -> dict[int, str]:
    order = np.argsort(centers[:, 1])
    return {
        int(cluster_id): SPECIES_BY_PETAL_ORDER[rank]
        for rank, cluster_id in enumerate(order)
    }


def cluster_iris(*, random_state: int = 42) -> ClusteringResult:
    X, y, feature_names, target_names = load_two_feature_dataset()
    kmeans = KMeans(n_clusters=3, n_init="auto", random_state=random_state)
    cluster_labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_
    centroid_species = _label_centroids_by_petal_length(centers)

    return ClusteringResult(
        kmeans=kmeans,
        cluster_labels=cluster_labels,
        centroid_species=centroid_species,
        feature_names=feature_names,
        centers=centers,
        ground_truth=y,
        target_names=target_names,
    )


def mapped_cluster_accuracy(result: ClusteringResult) -> float:
    species_to_idx = {name: idx for idx, name in enumerate(result.target_names)}
    mapped = np.array(
        [species_to_idx[result.centroid_species[label]] for label in result.cluster_labels]
    )
    return float(accuracy_score(result.ground_truth, mapped))


def plot_clusters(result: ClusteringResult, *, show: bool = True) -> plt.Figure:
    X, _, _, _ = load_two_feature_dataset()
    centers = result.centers

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(
        X[:, 0],
        X[:, 1],
        c=result.cluster_labels,
        s=60,
        cmap="viridis",
        alpha=0.8,
        label="Data points",
    )
    ax.scatter(
        centers[:, 0],
        centers[:, 1],
        marker="X",
        s=250,
        c="red",
        edgecolors="black",
        linewidths=1.5,
        label="Centroids",
        zorder=5,
    )

    for cluster_id, center in enumerate(centers):
        species = result.centroid_species[cluster_id]
        ax.annotate(
            species,
            (center[0], center[1]),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title("Iris K-Means Clustering (sepal length vs petal length)")
    ax.set_xlabel(result.feature_names[0])
    ax.set_ylabel(result.feature_names[1])
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if show:
        plt.show()
    return fig
