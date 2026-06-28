"""Toy spam email feature tables for exercises 03 and 04."""

from __future__ import annotations

import numpy as np

FEATURE_NAMES = ("contains_free", "many_exclamations")

# Exercise 03: decision tree table (includes one contradictory [0, 1] pair).
TREE_X = np.array(
    [
        [1, 1],
        [1, 0],
        [1, 1],
        [1, 0],
        [0, 1],
        [0, 1],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
    ],
    dtype=int,
)
TREE_Y = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0], dtype=int)

# Exercise 04: random forest table (noisy row at index 4).
FOREST_X = np.array(
    [
        [1, 1],
        [1, 0],
        [1, 1],
        [0, 1],
        [0, 1],
        [0, 0],
        [0, 0],
        [1, 0],
        [0, 0],
        [1, 1],
    ],
    dtype=int,
)
FOREST_Y = np.array([1, 1, 1, 1, 0, 0, 0, 1, 0, 1], dtype=int)
