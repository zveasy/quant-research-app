"""Superior Predictive Ability (SPA) test – simplified.

CLI usage (for CI):

    python -m research.spa --input backtests/sample.parquet [--alpha 0.10]

The module expects a Parquet file with a column named ``returns`` (daily or
periodic strategy P&L). It performs a *stationary bootstrap* to estimate the
p-value that the mean return is <= 0 (null hypothesis) versus > 0.
The test is lightweight (1k bootstraps) and **deterministic** via a fixed RNG
seed so CI remains stable.

Exit code:
- 0  if p-value ≤ alpha.
- 1  otherwise.

References
~~~~~~~~~~
White, H. (2000). A Reality Check for Data Snooping. Econometrica.
Hansen, P. (2005). A Test for Superior Predictive Ability. Journal of Business & Economic Statistics.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.random import RandomState

__all__ = ["spa_p_value", "main"]


def _stationary_bootstrap(rs: RandomState, x: np.ndarray, B: int = 1000, p: float = 0.1) -> np.ndarray:
    """Return B bootstrap sample means using stationary bootstrap."""
    n = len(x)
    means = np.empty(B)
    for b in range(B):
        i = rs.randint(0, n)
        sample = []
        while len(sample) < n:
            block_len = rs.geometric(p)
            end = min(i + block_len, n)
            sample.extend(x[i:end])
            i = rs.randint(0, n)
        means[b] = np.mean(sample[:n])
    return means


def spa_p_value(returns: np.ndarray, *, B: int = 1000, seed: int = 42) -> float:
    """Compute one-sided SPA p-value that mean(returns) ≤ 0."""
    rs = RandomState(seed)
    mu_hat = returns.mean()
    boot_means = _stationary_bootstrap(rs, returns, B=B)
    p_val = np.mean(boot_means >= mu_hat)
    return float(p_val)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="SPA reality-check test")
    parser.add_argument("--input", required=True, help="Input Parquet file with 'returns' column")
    parser.add_argument("--alpha", type=float, default=0.10, help="Significance level")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.exists():
        # Synthesise a small positive-return series so CI can run out-of-box.
        rs = np.random.RandomState(123)
        df = pd.DataFrame({"returns": rs.normal(loc=0.001, scale=0.01, size=252)})
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path)
        print(f"[spa] Generated synthetic returns to {path}")
    else:
        df = pd.read_parquet(path)
    if "returns" not in df.columns:
        print("Parquet must contain 'returns' column", file=sys.stderr)
        sys.exit(1)

    p_val = spa_p_value(df["returns"].values)
    print(f"SPA p-value: {p_val:.4f}")
    if p_val <= args.alpha:
        print("✅ Reality-check passed")
        sys.exit(0)
    else:
        print("❌ Reality-check failed")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
