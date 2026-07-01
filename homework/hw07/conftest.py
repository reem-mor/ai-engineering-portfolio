"""Pytest configuration for hw07 — adds project root to import path."""

from __future__ import annotations

import sys
from pathlib import Path

HW07_ROOT = Path(__file__).resolve().parent
if str(HW07_ROOT) not in sys.path:
    sys.path.insert(0, str(HW07_ROOT))
