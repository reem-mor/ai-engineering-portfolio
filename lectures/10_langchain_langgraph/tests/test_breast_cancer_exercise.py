"""Offline tests for the breast cancer exercise."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.breast_cancer_model import (
    FEATURE_NAMES,
    load_two_feature_dataset,
    predict_diagnosis,
    summarize_dataset,
    train_classifier,
)


def test_dataset_has_expected_features() -> None:
    summary = summarize_dataset()
    assert summary.feature_names == FEATURE_NAMES
    assert summary.n_samples == 569
    assert summary.malignant_count + summary.benign_count == summary.n_samples


def test_train_classifier_accuracy() -> None:
    result = train_classifier()
    # Two-feature model; ~88% is expected on this holdout split.
    assert result.test_accuracy >= 0.85


def test_predict_returns_valid_label() -> None:
    X, _, target_names = load_two_feature_dataset()
    result = train_classifier()
    mean_radius, mean_texture = X[0]
    label, confidence = predict_diagnosis(
        result.pipeline,
        target_names,
        float(mean_radius),
        float(mean_texture),
    )
    assert label in target_names
    assert 0.0 <= confidence <= 1.0


def test_predict_shape_is_single_sample() -> None:
    result = train_classifier()
    sample = np.array([[17.99, 10.38]])
    pred = result.pipeline.predict(sample)
    assert pred.shape == (1,)
