"""Stress testing utilities."""

from __future__ import annotations
import numpy as np
import pandas as pd


def monte_carlo_stress(returns_df: pd.DataFrame, horizon: int = 10, paths: int = 2500) -> np.ndarray:
    """Simulate price paths via geometric Brownian motion.

    Parameters
    ----------
    returns_df : DataFrame
        Historical daily returns with asset columns.
    horizon : int
        Number of steps to simulate.
    paths : int
        Number of Monte Carlo paths.

    Returns
    -------
    np.ndarray
        Array of shape ``(paths, horizon, n_symbols)``.
    """
    mu = returns_df.mean().to_numpy()
    sigma = returns_df.std().to_numpy()
    n = len(mu)
    rand = np.random.standard_normal((paths, horizon, n))
    drift = (mu - 0.5 * sigma**2)[None, None, :]
    step = drift + sigma[None, None, :] * rand
    log_paths = np.cumsum(step, axis=1)
    return np.exp(log_paths)


def var95(paths: np.ndarray, initial: float = 1.0) -> np.ndarray:
    """Compute the 95%% Value-at-Risk for the final step."""
    pnl = paths[:, -1, :] * initial - initial
    return np.percentile(pnl, 5, axis=0)
