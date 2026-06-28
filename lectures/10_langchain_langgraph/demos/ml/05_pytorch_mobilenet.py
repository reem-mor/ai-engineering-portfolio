"""PyTorch demo: pretrained MobileNetV3 image classification (ImageNet top-k)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from exercises.mobilenet_model import (
    get_device,
    load_mobilenet,
    predict_image_path,
    predictions_to_json,
)
from lecture_config import SAMPLE_IMAGE

TOPK = 5
FORCE_CPU = False
DEFAULT_IMAGE = SAMPLE_IMAGE


def main() -> None:
    image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IMAGE

    device = get_device(force_cpu=FORCE_CPU)
    print("CUDA available:", torch.cuda.is_available())
    print("Using device:", device)

    model, preprocess, labels = load_mobilenet(device)
    print("Model device:", next(model.parameters()).device)
    print("Image path:", image_path)

    predictions = predict_image_path(
        model,
        preprocess,
        labels,
        image_path,
        device,
        topk=TOPK,
    )
    print(json.dumps(predictions_to_json(predictions), indent=2))


if __name__ == "__main__":
    main()
