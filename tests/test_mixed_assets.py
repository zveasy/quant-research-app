import pandas as pd
import numpy as np
import duckdb
import types
import sys

import pytest

# Import inside the test to allow monkeypatching vectorbt if missing

@pytest.fixture
def setup_dummy_database(tmp_path):
    db_path = tmp_path / "test_asset_universe.duckdb"
    dummy_candidates = [
        {"symbol": "AAPL", "fit_score": 90},
        {"symbol": "GOOG", "fit_score": 85},
    ]
    df = pd.DataFrame(dummy_candidates)
    con = duckdb.connect(database=str(db_path), read_only=False)
    con.register('candidates_df_view', df)
    con.execute("CREATE OR REPLACE TABLE candidates AS SELECT * FROM candidates_df_view")
    con.close()
    return str(db_path)


def create_fake_vectorbt(monkeypatch):
    fake_vbt = types.SimpleNamespace()

    class FakeMA:
        def __init__(self, ma):
            self.ma = ma

        @classmethod
        def run(cls, price, window):
            return cls(price.rolling(window).mean())

        def ma_crossed_above(self, other):
            return self.ma > other.ma

        def ma_crossed_below(self, other):
            return self.ma < other.ma

    class FakePF:
        @classmethod
        def from_signals(cls, price, entries, exits, **kwargs):
            return types.SimpleNamespace(stats=lambda: pd.DataFrame({"Total Return [%]": [5.0]}))

    fake_vbt.MA = FakeMA
    fake_vbt.Portfolio = FakePF
    monkeypatch.setitem(sys.modules, 'vectorbt', fake_vbt)
    return fake_vbt


def fake_download(symbols, start=None, end=None, period=None, auto_adjust=True):
    import pandas as pd
    if isinstance(symbols, str):
        syms = [symbols]
    else:
        syms = list(symbols)
    dates = pd.date_range(start or '2023-01-01', periods=10, freq='D')
    # Create a DataFrame with a 'Close' column for each symbol
    data = {s: np.linspace(100, 110, num=len(dates)) for s in syms}
    df = pd.DataFrame(data, index=dates)
    # If the code expects a MultiIndex, add it; otherwise, keep single-level columns
    df.columns.name = None
    # Add a 'Close' column if needed for compatibility
    if 'Close' not in df.columns:
        df['Close'] = 100
    return df


def test_mixed_asset_backtest(monkeypatch, setup_dummy_database, capsys):
    monkeypatch.setattr('backtester.core.DB_FILE', setup_dummy_database)
    monkeypatch.setattr('yfinance.download', fake_download)
    create_fake_vectorbt(monkeypatch)
    from backtester.core import run_crossover_backtest

    run_crossover_backtest(2, 3, start_date='2023-01-01', end_date='2023-01-10', asset_classes=['equity', 'crypto'])
    captured = capsys.readouterr()
    assert 'Performance Summary' in captured.out
