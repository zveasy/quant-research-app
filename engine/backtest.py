"""Minimal deterministic back-test stub used solely for CI determinism harness.

The real engine will replace this module. For now we simulate a tiny strategy
with deterministic returns driven by a fixed RNG seed so two consecutive runs
produce byte-identical Parquet output.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import io
from typing import Tuple

import numpy as np
import pandas as pd

__all__ = ["run_backtest", "DATA_COLS", "write_parquet", "parquet_sha256"]

DATA_COLS = ["ts", "pnl", "position"]


def _generate_df(n: int = 10, seed: int = 42) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    ts = pd.date_range("2024-01-01", periods=n, freq="D")
    pnl = rng.randn(n).round(6)
    position = rng.randint(-1, 2, size=n)
    return pd.DataFrame({"ts": ts, "pnl": pnl, "position": position})


def run_backtest(*, n: int = 10, seed: int = 42) -> pd.DataFrame:
    """Return deterministic back-test results as DataFrame."""
    return _generate_df(n=n, seed=seed)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write DataFrame to Parquet with stable dtypes & metadata order."""
    df = df[DATA_COLS]  # ensure column order
    df.to_parquet(path, engine="pyarrow", index=False)


def parquet_sha256(df: pd.DataFrame) -> str:
    """Return SHA-256 hex digest of the Parquet representation (in-memory)."""
    buf = io.BytesIO()
    df.to_parquet(buf, engine="pyarrow", index=False)
    return hashlib.sha256(buf.getvalue()).hexdigest()
