import pandas as pd
import numpy as np
from factors.momentum import compute_momentum


def test_compute_momentum_basic():
    dates = pd.date_range('2022-01-01', periods=60)
    price = pd.DataFrame({
        'AAA': np.linspace(100, 120, 60),
        'BBB': np.linspace(100, 80, 60)
    }, index=dates)

    result = compute_momentum(price, lookback=20)
    assert set(result.columns) == {'date', 'symbol', 'momentum_z'}

    last_date = result['date'].max()
    manual = price.shift(21) / price.shift(41) - 1
    manual_last = manual.loc[last_date]
    rank_last = manual_last.rank()
    z_last = (rank_last - rank_last.mean()) / rank_last.std(ddof=0)

    expected = z_last.rename('momentum_z').reset_index()
    expected.columns = ['symbol', 'momentum_z']
    expected['date'] = last_date
    expected = expected[['date', 'symbol', 'momentum_z']]

    pd.testing.assert_frame_equal(
        result[result['date'] == last_date].sort_values('symbol').reset_index(drop=True),
        expected.sort_values('symbol').reset_index(drop=True)
    )
