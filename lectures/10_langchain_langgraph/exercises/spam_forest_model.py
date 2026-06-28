"""Spam random forest helpers for exercise 04 and tests."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from exercises.spam_email_data import FEATURE_NAMES, FOREST_X, FOREST_Y


@dataclass(frozen=True)
class ForestTrainingResult:
    classifier: RandomForestClassifier
    training_accuracy: float
    feature_importances: np.ndarray
    feature_names: tuple[str, ...]


def train_spam_forest(
    *,
    random_state: int = 42,
    n_estimators: int = 50,
) -> ForestTrainingResult:
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=None,
        random_state=random_state,
    )
    clf.fit(FOREST_X, FOREST_Y)
    training_accuracy = float(accuracy_score(FOREST_Y, clf.predict(FOREST_X)))
    return ForestTrainingResult(
        classifier=clf,
        training_accuracy=training_accuracy,
        feature_importances=clf.feature_importances_.copy(),
        feature_names=FEATURE_NAMES,
    )


def predict_spam(
    classifier: RandomForestClassifier,
    contains_free: int,
    many_exclamations: int,
    *,
    threshold: float = 0.5,
) -> tuple[int, float]:
    sample = np.array([[contains_free, many_exclamations]], dtype=int)
    spam_score = float(classifier.predict_proba(sample)[0, 1])
    label = int(spam_score >= threshold)
    return label, spam_score
