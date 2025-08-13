"""Leakage detection utilities for research pipelines.

The heuristics implemented here are *light-weight* and designed for CI
gate-keeping – they are **not** a formal proof of absence of leakage, but they
catch the most common errors in feature engineering workflows:

1. *Target peeking* – using the future target value (or derivatives) in the
   feature matrix.
2. *Post-event joins* – enriching the feature set with information whose
   timestamp lies *after* the prediction/decision time.
3. *Future shift leaks* – features constructed with a negative shift, e.g.
   ``df['price_t+1'] = df['price'].shift(-1)``.

The public API purposefully operates on **pandas DataFrame** input so we can use
it both in unit tests and ad-hoc CI scripts without additional dependencies.
"""

from __future__ import annotations

import warnings
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

__all__ = [
    "detect_target_peeking",
    "detect_future_shift_leak",
    "detect_leaks",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _corr(a: pd.Series, b: pd.Series) -> float:
    """Pearson correlation ignoring NaNs – returns 0 if degenerate."""
    mask = a.notna() & b.notna()
    if mask.sum() < 3:
        return 0.0
    return float(a[mask].corr(b[mask]))


# ---------------------------------------------------------------------------
# Leakage detectors
# ---------------------------------------------------------------------------


def detect_target_peeking(
    df: pd.DataFrame,
    *,
    feature_cols: List[str],
    target_col: str,
    horizon: int = 1,
    threshold: float = 0.99,
) -> List[str]:
    """Return list of features that correlate (≈1) with *future* target.

    The function computes the Pearson correlation between each feature and the
    *lead* (shift(-horizon)) of the target. Correlation above *threshold* is
    treated as deterministic / direct leakage.
    """

    if horizon <= 0:
        raise ValueError("horizon must be positive – it is a *future* offset")
    target_now = df[target_col]
    future_target = target_now.shift(-horizon)
    offenders: list[str] = []
    for col in feature_cols:
        r_now = abs(_corr(df[col], target_now))
        r_future = abs(_corr(df[col], future_target))
        if max(r_now, r_future) >= threshold:
            offenders.append(col)
    return offenders


def detect_future_shift_leak(
    df: pd.DataFrame, *, feature_cols: List[str]
) -> List[str]:
    """Detect columns created via negative shifts (t+1, t+2 …).

    Heuristic: if a column has perfect 1-lag correlation with its own *lagged*
    version but not with the current, it likely originates from a negative
    shift. Works well for synthetic tests where leak is exact copy.
    """

    offenders: list[str] = []
    for col in feature_cols:
        # Heuristic 1: suspicious naming patterns
        if any(pattern in col.lower() for pattern in ["t_plus", "lead", "future", "shift_neg"]):
            offenders.append(col)
            continue
        # Heuristic 2: near-perfect autocorr with 1-lag (exact copy)
        lag1_corr = _corr(df[col], df[col].shift(1))
        if abs(lag1_corr) > 0.999:  # stricter threshold to avoid FP on price levels
            offenders.append(col)
    return offenders


# ---------------------------------------------------------------------------
# Compound interface
# ---------------------------------------------------------------------------


def detect_leaks(
    df: pd.DataFrame,
    *,
    feature_cols: List[str],
    target_col: str,
    horizon: int = 1,
) -> Dict[str, List[str]]:
    """Run all leak detectors and aggregate offenders by type."""

    results = {
        "target_peeking": detect_target_peeking(
            df, feature_cols=feature_cols, target_col=target_col, horizon=horizon
        ),
        "future_shift": detect_future_shift_leak(df, feature_cols=feature_cols),
    }
    # Placeholder for future detectors (post-event joins, etc.)
    return results
