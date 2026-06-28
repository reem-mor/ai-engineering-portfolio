"""Breast cancer classification helpers for exercise 01 and tests."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = ("mean radius", "mean texture")


@dataclass(frozen=True)
class DatasetSummary:
    n_samples: int
    n_features: int
    feature_names: tuple[str, ...]
    target_names: tuple[str, ...]
    malignant_count: int
    benign_count: int


@dataclass(frozen=True)
class TrainingResult:
    pipeline: Pipeline
    target_names: tuple[str, ...]
    test_accuracy: float
    report: str


def load_two_feature_dataset() -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    data = load_breast_cancer()
    feature_indices = [
        list(data.feature_names).index(name) for name in FEATURE_NAMES
    ]
    X = data.data[:, feature_indices]
    y = data.target
    return X, y, tuple(data.target_names)


def summarize_dataset() -> DatasetSummary:
    X, y, target_names = load_two_feature_dataset()
    data = load_breast_cancer()
    malignant_count = int(np.sum(y == 0))
    benign_count = int(np.sum(y == 1))
    return DatasetSummary(
        n_samples=X.shape[0],
        n_features=len(data.feature_names),
        feature_names=FEATURE_NAMES,
        target_names=target_names,
        malignant_count=malignant_count,
        benign_count=benign_count,
    )


def train_classifier(
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> TrainingResult:
    X, y, target_names = load_two_feature_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=random_state)),
        ]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test,
        y_pred,
        target_names=list(target_names),
    )

    return TrainingResult(
        pipeline=pipeline,
        target_names=target_names,
        test_accuracy=accuracy,
        report=report,
    )


def predict_diagnosis(
    pipeline: Pipeline,
    target_names: tuple[str, ...],
    mean_radius: float,
    mean_texture: float,
) -> tuple[str, float]:
    sample = np.array([[mean_radius, mean_texture]])
    label_idx = int(pipeline.predict(sample)[0])
    proba = float(pipeline.predict_proba(sample)[0, label_idx])
    return target_names[label_idx], proba
