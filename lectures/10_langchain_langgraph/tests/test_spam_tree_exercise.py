"""Offline tests for the spam decision tree exercise."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.spam_tree_model import predict_spam, train_spam_tree


def test_rules_include_primary_split() -> None:
    result = train_spam_tree()
    assert "contains_free" in result.rules_text


def test_training_accuracy_on_tiny_table() -> None:
    result = train_spam_tree()
    assert result.training_accuracy == 0.9


def test_predict_contains_free_is_spam() -> None:
    result = train_spam_tree()
    label, leaf_vote = predict_spam(result.classifier, 1, 0)
    assert label == 1
    assert leaf_vote == 1.0


def test_predict_no_features_is_not_spam() -> None:
    result = train_spam_tree()
    label, leaf_vote = predict_spam(result.classifier, 0, 0)
    assert label == 0
    assert leaf_vote == 0.0


def test_predict_ambiguous_branch() -> None:
    result = train_spam_tree()
    label, leaf_vote = predict_spam(result.classifier, 0, 1)
    assert label == 0
    assert leaf_vote == 0.5
