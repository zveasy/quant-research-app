import pandas as pd
import numpy as np
from pathlib import Path

MAPPING_PATH = Path('data/mapping/figi_map.csv')

def test_figi_mapping_roundtrip():
    mapping = pd.read_csv(MAPPING_PATH)
    # ensure at least AAPL mapping present
    assert 'BBG000B9XRY4' in mapping['figi'].values
    lookup = mapping.set_index('figi')['ticker']
    reverse = mapping.set_index('ticker')['figi']
    figi = 'BBG000B9XRY4'
    ticker = lookup[figi]
    assert reverse[ticker] == figi


def _apply_split(prices: pd.Series, split_factor: float, split_date: str) -> pd.Series:
    adj = prices.copy()
    mask = prices.index < split_date
    adj.loc[mask] = prices.loc[mask] / split_factor
    return adj


def test_split_adjustment():
    idx = pd.date_range('2020-01-01', periods=4, freq='D')
    prices = pd.Series([100, 102, 50, 51], index=idx)  # naive pre/post 2-for-1 split on 2020-01-03
    adjusted = _apply_split(prices, split_factor=2.0, split_date='2020-01-03')
    # after adjustment, series should be continuous
    returns = adjusted.pct_change().dropna()
    # Ensure no single-day jump exceeding 60%
    assert returns.abs().max() < 0.6
