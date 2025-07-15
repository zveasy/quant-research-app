"""GPU accelerated risk engine using CuPy."""

from __future__ import annotations

from typing import List, Tuple

import cupy as cp
import pandas as pd

from .scenario_dsl import Scenario


def compute_pnl(paths: cp.ndarray) -> cp.ndarray:
    return paths[:, -1] - paths[:, 0]


def run_engine(positions: pd.DataFrame, scenarios: List[Scenario]) -> Tuple[float, float, cp.ndarray]:
    n = 10000
    pnl_dist = cp.zeros(n)
    for s in scenarios:
        shocks = positions.copy()
        for f in s.shocks:
            shocks = shocks.applymap(f)
        paths = cp.asarray(shocks.values)[None, :, :] * cp.random.lognormal(0, 0.01, (n, shocks.shape[0], shocks.shape[1]))
        pnl_dist += compute_pnl(paths).sum(axis=1)
    var = float(cp.percentile(pnl_dist, 5))
    es = float(pnl_dist[pnl_dist <= var].mean())
    return var, es, pnl_dist
