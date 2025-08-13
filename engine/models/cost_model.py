"""Latency & slippage cost model (v1).

Implements the linear model described in `engine/fidelity.md` and provides
APIs to estimate implementation shortfall (IS) in basis points.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["CostModel", "load_fixture_logs", "mape"]

K0 = 1.2
K1 = 0.5
K2 = 0.9


@dataclass(frozen=True)
class CostModel:
    k0: float = K0
    k1: float = K1
    k2: float = K2

    def estimate_is(self, latency_ms: np.ndarray, spread_bps: np.ndarray) -> np.ndarray:
        """Return estimated IS in bps."""
        return self.k0 + self.k1 * spread_bps + self.k2 * (latency_ms / 1000.0)


# ---------------------------------------------------------------------------
# Fixture log utilities
# ---------------------------------------------------------------------------

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures/latency/sample_logs.csv"


def load_fixture_logs(path: Path = FIXTURE_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean absolute percentage error in %."""
    return float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)
