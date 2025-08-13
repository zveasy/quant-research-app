"""Capacity curve estimation utilities.

Given a table of executed *fills* with quantity (Q), fill price, and realised
slippage (bps), estimate the capacity curve – net PnL versus size – and output:

* **PNG** plot saved under ``docs/research/figs/capacity_curve.png``.
* **CSV** file with columns (Q, net_PnL, IS_bps) alongside the PNG.

This module contains both a programmatic API (`capacity_curve`) and a
command-line interface suitable for CI:

    python -m research.capacity --fills data/sample_fills.parquet

If the fills file is absent, the script generates a synthetic dataset so CI can
run without external artefacts.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FIG_DIR = Path("docs/research/figs")
FIG_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUT = FIG_DIR / "capacity_results.csv"
PNG_OUT = FIG_DIR / "capacity_curve.png"


def _load_fills(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    # synthesize simple fills for CI
    rng = np.random.RandomState(42)
    Q = np.linspace(1e3, 1e5, 20)
    # Assume linear + quadratic cost
    alpha, beta = 0.01, 1e-8  # impact parameters
    slippage_bps = alpha * Q + beta * Q ** 2
    price = 100.0
    net_pnl = price * Q * (0.002 - slippage_bps / 1e4)  # 20 bps alpha vs slippage
    df = pd.DataFrame({"Q": Q, "slippage_bps": slippage_bps, "net_PnL": net_pnl})
    return df


def capacity_curve(df: pd.DataFrame) -> pd.DataFrame:
    """Return DF with Q, net_PnL, IS_bps and save PNG + CSV side-effects."""
    if not {"Q", "net_PnL"}.issubset(df.columns):
        raise ValueError("fills data must have Q and net_PnL columns")
    # Compute in-sample bps
    df = df.copy()
    df["IS_bps"] = 1e4 * df["net_PnL"] / (df["Q"] * 100)  # assuming $100 price

    # Plot
    plt.figure(figsize=(6, 4))
    plt.plot(df["Q"], df["net_PnL"], marker="o")
    plt.xlabel("Quantity (shares)")
    plt.ylabel("Net PnL ($)")
    plt.title("Capacity Curve")
    plt.grid(True, ls=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(PNG_OUT)
    plt.close()

    df.to_csv(CSV_OUT, index=False)
    print(f"[capacity] Saved curve to {PNG_OUT} and CSV to {CSV_OUT}")
    return df


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Capacity curve estimation")
    parser.add_argument("--fills", default="data/sample_fills.parquet", help="Path to fills data")
    args = parser.parse_args(argv)
    fills_path = Path(args.fills)
    df_fills = _load_fills(fills_path)
    capacity_curve(df_fills)


if __name__ == "__main__":  # pragma: no cover
    main()
