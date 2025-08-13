import numpy as np
import pandas as pd
from data.bad_tick_filter import is_bad_tick, count_bad_ticks


def _sample_series(n=1000, n_bad=25):
    rng = np.random.RandomState(1)
    price = pd.Series(100 + rng.randn(n).cumsum() * 0.01, name="price")
    bad_idx = rng.choice(n, size=n_bad, replace=False)
    price.iloc[bad_idx] *= 10  # spikes
    return price


def test_bad_tick_count():
    series = _sample_series()
    bad_mask = is_bad_tick(series, max_rel_change=0.2)
    assert bad_mask.sum() >= 25  # at least the spikes
    total = count_bad_ticks(series, max_rel_change=0.2)
    assert total == bad_mask.sum()
