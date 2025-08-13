"""Utilities for in-sample / out-of-sample splitting and walk-forward validation.

The split helpers work with **pandas DataFrame** or **Series** indexed by datetime
(or an index that is sorted, regular, and monotonic).

Main helpers
~~~~~~~~~~~~
walk_forward_splits(index, train_size, test_size, step=None, drop_remainder=True)
    Generate successive (train_mask, test_mask) boolean arrays for walk-forward
    evaluation.

train_test_split(index, test_size)
    Simple hold-out split preserving order.

The functions intentionally operate on an **index** (e.g. `df.index`) to keep side
effects minimal and avoid copying heavy market-data payloads around.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd

__all__ = [
    "train_test_split",
    "walk_forward_splits",
]


def _validate_index(index: pd.Index) -> None:
    if not isinstance(index, pd.Index):
        raise TypeError("index must be a pandas Index")
    if not index.is_monotonic_increasing:
        raise ValueError("index must be sorted ascending for time-series splits")


def train_test_split(
    index: pd.Index, *, test_size: int | float = 0.2
) -> Tuple[np.ndarray, np.ndarray]:
    """Return boolean masks for a simple IS / OOS split.

    Parameters
    ----------
    index
        Sorted, monotonic index of the dataset.
    test_size
        If **float**, interpreted as the fraction of observations in the test / OOS
        set (0 < test_size < 1). If **int**, interpreted as an *absolute* number of
        trailing observations.
    Returns
    -------
    train_mask, test_mask : np.ndarray, np.ndarray
        Boolean arrays such that they are **mutually exclusive** and
        `train_mask | test_mask` is all True.
    """

    _validate_index(index)

    n = len(index)
    if isinstance(test_size, float):
        if not 0.0 < test_size < 1.0:
            raise ValueError("test_size fraction must be between 0 and 1")
        k = math.ceil(n * test_size)
    else:
        k = int(test_size)
        if k <= 0 or k >= n:
            raise ValueError("test_size int must be between 1 and n-1")

    test_mask = np.zeros(n, dtype=bool)
    test_mask[-k:] = True
    train_mask = ~test_mask
    return train_mask, test_mask


def walk_forward_splits(
    index: pd.Index,
    *,
    train_size: int,
    test_size: int,
    step: int | None = None,
    drop_remainder: bool = True,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Generate walk-forward train / test boolean masks.

    Parameters
    ----------
    index
        Sorted, monotonic index.
    train_size
        Number of observations in each training (IS) window.
    test_size
        Number of observations in each test (OOS) window.
    step
        How far to slide the window after each iteration. Defaults to *test_size*
        (non-overlapping test sets).
    drop_remainder
        If *True*, incomplete windows at the tail are dropped. If *False*, the
        last window that would be shorter than *test_size* is still yielded.
    Returns
    -------
    List of tuples ``(train_mask, test_mask)``.
    """

    _validate_index(index)
    n = len(index)
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive")
    step = test_size if step is None else step
    if step <= 0:
        raise ValueError("step must be positive")

    splits: list[tuple[np.ndarray, np.ndarray]] = []
    start = 0
    while True:
        train_start = start
        train_end = train_start + train_size  # exclusive
        test_start = train_end
        test_end = test_start + test_size

        if test_start >= n:
            break  # no room for test set
        if test_end > n and drop_remainder:
            break

        train_mask = np.zeros(n, dtype=bool)
        test_mask = np.zeros(n, dtype=bool)
        train_mask[train_start: min(train_end, n)] = True
        test_mask[test_start: min(test_end, n)] = True
        splits.append((train_mask, test_mask))

        if test_end >= n:
            break
        start += step

    return splits
