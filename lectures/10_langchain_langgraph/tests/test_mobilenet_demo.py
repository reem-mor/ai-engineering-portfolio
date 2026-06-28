"""Offline tests for the PyTorch MobileNet demo."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.mobilenet_model import (
    get_device,
    load_mobilenet,
    predict_image_bytes,
    predict_image_path,
    predictions_to_json,
)
from lecture_config import SAMPLE_IMAGE


def _solid_rgb_bytes(color: tuple[int, int, int] = (120, 80, 200)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (224, 224), color).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_get_device_respects_force_cpu() -> None:
    assert get_device(force_cpu=True) == torch.device("cpu")


def test_sample_image_exists() -> None:
    assert SAMPLE_IMAGE.exists(), f"Expected sample image at {SAMPLE_IMAGE}"


def test_predictions_to_json_format() -> None:
    from exercises.mobilenet_model import ImagePrediction

    payload = predictions_to_json(
        [ImagePrediction(label="tabby", prob=0.42), ImagePrediction(label="tiger", prob=0.21)]
    )
    assert payload == [{"label": "tabby", "prob": 0.42}, {"label": "tiger", "prob": 0.21}]


def test_predict_image_path_missing_file(tmp_path: Path) -> None:
    device = get_device(force_cpu=True)
    model, preprocess, labels = load_mobilenet(device)
    missing = tmp_path / "missing.jpg"
    with pytest.raises(FileNotFoundError, match="Image not found"):
        predict_image_path(model, preprocess, labels, missing, device, topk=3)


def test_mobilenet_topk_predictions() -> None:
    device = get_device(force_cpu=True)
    model, preprocess, labels = load_mobilenet(device)

    predictions = predict_image_bytes(
        model,
        preprocess,
        labels,
        _solid_rgb_bytes(),
        device,
        topk=5,
    )

    assert len(predictions) == 5
    assert all(0.0 <= item.prob <= 1.0 for item in predictions)
    assert all(item.label in labels for item in predictions)
    assert predictions[0].prob >= predictions[-1].prob


def test_mobilenet_predicts_sample_image() -> None:
    device = get_device(force_cpu=True)
    model, preprocess, labels = load_mobilenet(device)

    predictions = predict_image_path(
        model,
        preprocess,
        labels,
        SAMPLE_IMAGE,
        device,
        topk=3,
    )

    assert len(predictions) == 3
    assert sum(item.prob for item in predictions) <= 1.0
