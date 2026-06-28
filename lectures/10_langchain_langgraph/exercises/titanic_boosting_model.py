"""Titanic gradient boosting helpers for exercise 05 and tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from lecture_config import TITANIC_CSV

FEATURE_NAMES: tuple[str, ...] = ("is_female", "is_child", "is_first_class")
EXAMPLE_FEATURES: tuple[int, int, int] = (1, 0, 1)


@dataclass(frozen=True)
class BoostingResult:
    name: str
    accuracy: float
    feature_importances: dict[str, float]
    example_prob: float


@dataclass(frozen=True)
class TitanicFeatureData:
    features: np.ndarray
    labels: np.ndarray
    feature_names: tuple[str, ...]
    feature_frame: pd.DataFrame


def _require_titanic_csv(csv_path: Path = TITANIC_CSV) -> Path:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Titanic dataset not found at: {csv_path}. "
            "Expected the shared hw03 dataset at homework/hw03/data/titanic.csv."
        )
    return csv_path


def load_titanic_features(
    *,
    csv_path: Path = TITANIC_CSV,
) -> TitanicFeatureData:
    path = _require_titanic_csv(csv_path)
    df = pd.read_csv(path)[["sex", "age", "pclass", "survived"]].copy()

    df["sex"] = df["sex"].astype(str).str.lower().str.strip()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["pclass"] = pd.to_numeric(df["pclass"], errors="coerce")
    df["survived"] = pd.to_numeric(df["survived"], errors="coerce").fillna(0).astype(int)

    df["age"] = df["age"].fillna(df["age"].median())
    df["pclass"] = df["pclass"].fillna(df["pclass"].mode()[0])

    feature_frame = pd.DataFrame(
        {
            "is_female": (df["sex"] == "female").astype(int),
            "is_child": (df["age"] < 16).astype(int),
            "is_first_class": (df["pclass"] == 1).astype(int),
        }
    )

    return TitanicFeatureData(
        features=feature_frame.values,
        labels=df["survived"].values,
        feature_names=FEATURE_NAMES,
        feature_frame=feature_frame.assign(survived=df["survived"].values),
    )


def split_titanic_features(
    data: TitanicFeatureData,
    *,
    test_size: float = 0.25,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return train_test_split(
        data.features,
        data.labels,
        test_size=test_size,
        random_state=random_state,
        stratify=data.labels,
    )


def _fit_xgb(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    *,
    n_estimators: int,
    random_state: int,
) -> XGBClassifier:
    xgb = XGBClassifier(
        n_estimators=n_estimators,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=random_state,
    )

    xgb_callbacks = []
    try:
        from xgboost.callback import EarlyStopping as XGBEarlyStopping

        xgb_callbacks = [XGBEarlyStopping(rounds=50, save_best=True, maximize=False)]
    except Exception:
        xgb_callbacks = []

    try:
        xgb.fit(
            x_train,
            y_train,
            eval_set=[(x_val, y_val)],
            callbacks=xgb_callbacks,
        )
    except TypeError:
        xgb.fit(x_train, y_train, eval_set=[(x_val, y_val)])

    return xgb


def _fit_lightgbm(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    *,
    n_estimators: int,
    random_state: int,
) -> LGBMClassifier:
    try:
        from lightgbm import early_stopping, log_evaluation
    except ImportError:
        from lightgbm.callback import early_stopping, log_evaluation

    lgbm = LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=random_state,
    )

    try:
        lgbm.fit(
            x_train,
            y_train,
            eval_set=[(x_val, y_val)],
            callbacks=[early_stopping(stopping_rounds=50), log_evaluation(period=0)],
        )
    except TypeError:
        lgbm.fit(x_train, y_train, eval_set=[(x_val, y_val)])

    return lgbm


def _fit_catboost(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    *,
    n_estimators: int,
    random_state: int,
) -> CatBoostClassifier:
    cat = CatBoostClassifier(
        iterations=n_estimators,
        learning_rate=0.05,
        depth=4,
        loss_function="Logloss",
        random_state=random_state,
        verbose=False,
    )

    try:
        cat.fit(
            x_train,
            y_train,
            eval_set=(x_val, y_val),
            early_stopping_rounds=50,
            verbose=False,
        )
    except TypeError:
        cat.fit(x_train, y_train, eval_set=(x_val, y_val), verbose=False)

    return cat


def _example_probability(model, example: tuple[int, int, int]) -> float:
    return float(model.predict_proba([list(example)])[0, 1])


def _importance_dict(
    feature_names: tuple[str, ...],
    importances: np.ndarray,
) -> dict[str, float]:
    return {
        name: float(value)
        for name, value in zip(feature_names, importances, strict=True)
    }


def train_all_boosters(
    data: TitanicFeatureData | None = None,
    *,
    n_estimators: int = 300,
    random_state: int = 42,
    test_size: float = 0.25,
) -> list[BoostingResult]:
    feature_data = data or load_titanic_features()
    x_train, x_val, y_train, y_val = split_titanic_features(
        feature_data,
        test_size=test_size,
        random_state=random_state,
    )

    results: list[BoostingResult] = []

    xgb = _fit_xgb(
        x_train,
        y_train,
        x_val,
        y_val,
        n_estimators=n_estimators,
        random_state=random_state,
    )
    xgb_pred = xgb.predict(x_val)
    results.append(
        BoostingResult(
            name="XGBoost",
            accuracy=float(accuracy_score(y_val, xgb_pred)),
            feature_importances=_importance_dict(
                feature_data.feature_names,
                xgb.feature_importances_,
            ),
            example_prob=_example_probability(xgb, EXAMPLE_FEATURES),
        )
    )

    lgbm = _fit_lightgbm(
        x_train,
        y_train,
        x_val,
        y_val,
        n_estimators=n_estimators,
        random_state=random_state,
    )
    lgbm_pred = lgbm.predict(x_val)
    results.append(
        BoostingResult(
            name="LightGBM",
            accuracy=float(accuracy_score(y_val, lgbm_pred)),
            feature_importances=_importance_dict(
                feature_data.feature_names,
                lgbm.feature_importances_,
            ),
            example_prob=_example_probability(lgbm, EXAMPLE_FEATURES),
        )
    )

    cat = _fit_catboost(
        x_train,
        y_train,
        x_val,
        y_val,
        n_estimators=n_estimators,
        random_state=random_state,
    )
    cat_pred = cat.predict(x_val)
    try:
        cat_pred = cat_pred.astype(int)
    except Exception:
        pass
    results.append(
        BoostingResult(
            name="CatBoost",
            accuracy=float(accuracy_score(y_val, cat_pred)),
            feature_importances=_importance_dict(
                feature_data.feature_names,
                cat.get_feature_importance(),
            ),
            example_prob=_example_probability(cat, EXAMPLE_FEATURES),
        )
    )

    return results
