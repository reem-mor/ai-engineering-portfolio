"""MobileNetV3 image classification helpers for the PyTorch demo and tests."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torchvision.models as models
from PIL import Image


@dataclass(frozen=True)
class ImagePrediction:
    label: str
    prob: float


def get_device(*, force_cpu: bool = False) -> torch.device:
    if force_cpu:
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_mobilenet(device: torch.device) -> tuple[Any, Any, list[str]]:
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    model = models.mobilenet_v3_small(weights=weights).to(device).eval()
    preprocess = weights.transforms()
    labels = list(weights.meta["categories"])
    return model, preprocess, labels


@torch.no_grad()
def predict_image_bytes(
    model: Any,
    preprocess: Any,
    labels: list[str],
    image_bytes: bytes,
    device: torch.device,
    *,
    topk: int = 5,
) -> list[ImagePrediction]:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = preprocess(img).unsqueeze(0).to(device)
    logits = model(tensor)
    probs = logits.softmax(dim=1)[0]
    values, indices = probs.topk(topk)
    return [
        ImagePrediction(label=labels[int(index)], prob=float(prob))
        for prob, index in zip(values, indices, strict=True)
    ]


def predict_image_path(
    model: Any,
    preprocess: Any,
    labels: list[str],
    image_path: str | Path,
    device: torch.device,
    *,
    topk: int = 5,
) -> list[ImagePrediction]:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at: {path}")
    image_bytes = path.read_bytes()
    return predict_image_bytes(
        model,
        preprocess,
        labels,
        image_bytes,
        device,
        topk=topk,
    )


def predictions_to_json(predictions: list[ImagePrediction]) -> list[dict[str, Any]]:
    return [{"label": item.label, "prob": item.prob} for item in predictions]
