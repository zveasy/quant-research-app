from __future__ import annotations

import cvxpy as cp
import pandas as pd


def esg_tilt_optimiser(df: pd.DataFrame) -> pd.DataFrame:
    """Optimise weights for ESG tilt.

    Expects DataFrame columns: weight, benchmark_weight, esg_score, sector.
    Returns DataFrame with column new_weight.
    """
    n = len(df)
    w = cp.Variable(n)
    benchmark = df["benchmark_weight"].values
    esg = df["esg_score"].values

    te = cp.sum_squares(w - benchmark)
    objective = cp.Minimize(te - 0.1 * esg @ w)

    constraints = [
        cp.sum(w) == 1,
        w >= 0,
        cp.abs(w - benchmark) <= 0.05,
        te <= 0.02 ** 2,
    ]

    # sector deviation
    sectors = df["sector"].unique()
    for sec in sectors:
        idx = df["sector"] == sec
        constraints.append(cp.abs(cp.sum(w[idx]) - df.loc[idx, "benchmark_weight"].sum()) <= 0.03)

    problem = cp.Problem(objective, constraints)
    problem.solve()
    df = df.copy()
    df["new_weight"] = w.value
    return df[["new_weight"]]
