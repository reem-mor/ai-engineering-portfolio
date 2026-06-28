"""Offline tests for the Titanic gradient boosting exercise."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.titanic_boosting_model import (
    EXAMPLE_FEATURES,
    FEATURE_NAMES,
    load_titanic_features,
    split_titanic_features,
    train_all_boosters,
)
from lecture_config import TITANIC_CSV


def test_titanic_csv_exists() -> None:
    assert TITANIC_CSV.exists(), f"Expected Titanic dataset at {TITANIC_CSV}"


def test_feature_matrix_shape_and_values() -> None:
    data = load_titanic_features()
    assert data.features.shape == (len(data.labels), 3)
    assert data.feature_names == FEATURE_NAMES
    assert set(np.unique(data.features)).issubset({0, 1})


def test_stratified_split_is_reproducible() -> None:
    data = load_titanic_features()
    first = split_titanic_features(data, random_state=42)
    second = split_titanic_features(data, random_state=42)
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])
    assert np.array_equal(first[2], second[2])
    assert np.array_equal(first[3], second[3])


@pytest.mark.parametrize("n_estimators", [50])
def test_all_boosters_meet_accuracy_floor(n_estimators: int) -> None:
    results = train_all_boosters(n_estimators=n_estimators, random_state=42)
    assert len(results) == 3
    for result in results:
        assert result.accuracy > 0.75
        assert set(result.feature_importances) == set(FEATURE_NAMES)
        assert 0.0 < result.example_prob < 1.0


def test_example_probability_uses_expected_features() -> None:
    results = train_all_boosters(n_estimators=50, random_state=42)
    for result in results:
        assert isinstance(result.example_prob, float)
        assert result.name in {"XGBoost", "LightGBM", "CatBoost"}


def test_missing_dataset_raises_clear_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError, match="Titanic dataset not found"):
        load_titanic_features(csv_path=missing)


def test_example_features_match_exercise_contract() -> None:
    assert EXAMPLE_FEATURES == (1, 0, 1)
