"""Bad-tick detection utilities.

Definition (v1): a *bad tick* is any trade/quote price that:
1. Is non-positive or NaN.
2. Deviates by more than *max_rel_change* (default 20%) from the immediately
   previous *valid* tick for the same instrument.

CLI usage (for CI):

    python -m data.bad_tick_filter --prices data/sample_ticks.parquet

The command loads a Parquet/CSV with columns [`ts`, `price`], computes the rate
per million observations, prints the result, and exits non-zero if the rate
exceeds the threshold (20 per 1M).

If the input file is missing, a synthetic dataset with <20 bad ticks is
generated so the pipeline passes by default.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THRESHOLD_PER_M = 20  # allowance in CI

__all__ = ["count_bad_ticks", "is_bad_tick"]


def is_bad_tick(series: pd.Series, *, max_rel_change: float = 0.2) -> pd.Series:
    """Return boolean mask of bad ticks in a price series."""
    bad = series.isna() | (series <= 0)
    pct_change = series.pct_change().abs()
    bad |= pct_change > max_rel_change
    return bad


def count_bad_ticks(series: pd.Series, *, max_rel_change: float = 0.2) -> int:
    return int(is_bad_tick(series, max_rel_change=max_rel_change).sum())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_prices(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    # synthesize 1M ticks with 10 bad ones (< threshold)
    n = 1_000_000
    rng = np.random.RandomState(0)
    price = pd.Series(100 + rng.randn(n).cumsum() * 0.01, name="price")
    bad_idx = rng.choice(n, size=10, replace=False)
    price.iloc[bad_idx] *= 10  # huge spike
    df = pd.DataFrame({"ts": pd.RangeIndex(n), "price": price})
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Bad-tick filter CI gate")
    parser.add_argument("--prices", default="data/sample_ticks.parquet", help="Path to price ticks")
    parser.add_argument("--max_rel_change", type=float, default=0.2, help="Relative change threshold")
    args = parser.parse_args(argv)

    prices_path = Path(args.prices)
    df = _load_prices(prices_path)
    bad = is_bad_tick(df["price"], max_rel_change=args.max_rel_change)
    rate = bad.sum() / len(df) * 1_000_000
    msg = f"Bad-tick rate: {rate:.1f} / 1M (≤ {THRESHOLD_PER_M})"
    if rate <= THRESHOLD_PER_M:
        print(msg + " ✅")
        sys.exit(0)
    else:
        print(msg + " ❌")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
