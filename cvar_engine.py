"""Compute Climate-VaR using Monte Carlo simulations."""
from __future__ import annotations

import os

import pandas as pd

try:
    import cupy as xp
except Exception:  # pragma: no cover
    import numpy as xp  # type: ignore


def compute_cvar(emissions: pd.DataFrame, confidence: float = 0.95, n_paths: int = 10000) -> pd.DataFrame:
    n_assets = emissions.shape[1]
    mu = -emissions.values.mean(axis=0) / 1e6
    sigma = emissions.values.std(axis=0) / 1e6
    paths = xp.random.normal(mu, sigma, size=(n_paths, n_assets))
    portfolio = paths.sum(axis=1)
    cutoff = int((1 - confidence) * n_paths)
    worst = xp.sort(portfolio)[:cutoff]
    cvar = float(xp.mean(worst))
    asset_cvar = xp.mean(xp.sort(paths, axis=0)[:cutoff], axis=0)
    df = pd.DataFrame({"CVaR_pct": asset_cvar.get() if hasattr(asset_cvar, 'get') else asset_cvar}, index=emissions.columns)
    df.loc["portfolio"] = cvar
    return df
