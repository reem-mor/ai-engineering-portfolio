"""Spam decision tree helpers for exercise 03 and tests."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier, export_text

from exercises.spam_email_data import FEATURE_NAMES, TREE_X, TREE_Y


@dataclass(frozen=True)
class TreeTrainingResult:
    classifier: DecisionTreeClassifier
    rules_text: str
    training_accuracy: float
    feature_names: tuple[str, ...]


def train_spam_tree(*, random_state: int = 0, max_depth: int = 2) -> TreeTrainingResult:
    clf = DecisionTreeClassifier(
        max_depth=max_depth,
        criterion="gini",
        random_state=random_state,
    )
    clf.fit(TREE_X, TREE_Y)
    rules = export_text(clf, feature_names=list(FEATURE_NAMES))
    training_accuracy = float(accuracy_score(TREE_Y, clf.predict(TREE_X)))
    return TreeTrainingResult(
        classifier=clf,
        rules_text=rules,
        training_accuracy=training_accuracy,
        feature_names=FEATURE_NAMES,
    )


def predict_spam(
    classifier: DecisionTreeClassifier,
    contains_free: int,
    many_exclamations: int,
) -> tuple[int, float]:
    sample = np.array([[contains_free, many_exclamations]], dtype=int)
    leaf_vote = float(classifier.predict_proba(sample)[0, 1])
    label = int(classifier.predict(sample)[0])
    return label, leaf_vote
