import pandas as pd
import numpy as np
from research.leak_checks import detect_leaks, detect_target_peeking, detect_future_shift_leak


def _synthetic_df(n=100):
    rng = np.random.RandomState(42)
    idx = pd.date_range("2021-01-01", periods=n, freq="D")
    price = pd.Series(rng.randn(n).cumsum() + 100, index=idx, name="price")
    target = price.pct_change().shift(-1).fillna(0.0)  # future return

    # Feature 1 – legitimate lagged return (OK)
    f_lag_ret = target.shift(1).rename("lag_ret")

    # Feature 2 – **leaky** direct copy of future target (peeking)
    f_peek = target.rename("peek_ret")

    # Feature 3 – **leaky** negative shift of price
    f_shift_leak = price.shift(-1).rename("price_t_plus_1")

    df = pd.concat([price, target.rename("target"), f_lag_ret, f_peek, f_shift_leak], axis=1)
    return df


def test_detects_leaks():
    df = _synthetic_df()
    feature_cols = [c for c in df.columns if c not in {"target", "price"}]

    res = detect_leaks(df, feature_cols=feature_cols, target_col="target", horizon=1)

    assert "peek_ret" in res["target_peeking"]
    assert "price_t_plus_1" in res["future_shift"]


def test_no_false_positives_after_fix():
    df = _synthetic_df().copy()
    # Drop leaky columns
    df = df.drop(columns=["peek_ret", "price_t_plus_1"])
    feature_cols = [c for c in df.columns if c not in {"target", "price"}]

    res = detect_leaks(df, feature_cols=feature_cols, target_col="target", horizon=1)

    for offenders in res.values():
        assert offenders == []
