"""Offline tests for the spam random forest exercise."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.spam_email_data import FEATURE_NAMES
from exercises.spam_forest_model import predict_spam, train_spam_forest


def test_feature_names() -> None:
    result = train_spam_forest()
    assert result.feature_names == FEATURE_NAMES


def test_training_accuracy_on_tiny_table() -> None:
    result = train_spam_forest()
    # Noisy duplicate feature row limits perfect fit on this tiny table.
    assert result.training_accuracy == 0.9


def test_contains_free_has_higher_importance() -> None:
    result = train_spam_forest()
    free_idx = FEATURE_NAMES.index("contains_free")
    excl_idx = FEATURE_NAMES.index("many_exclamations")
    assert result.feature_importances[free_idx] >= result.feature_importances[excl_idx]


def test_predict_clear_spam() -> None:
    result = train_spam_forest()
    label, spam_score = predict_spam(result.classifier, 1, 1)
    assert label == 1
    assert spam_score > 0.5


def test_predict_clear_not_spam() -> None:
    result = train_spam_forest()
    label, spam_score = predict_spam(result.classifier, 0, 0)
    assert label == 0
    assert spam_score < 0.5
