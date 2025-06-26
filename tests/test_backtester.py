# In: tests/test_backtester.py

import pytest
import duckdb
import pandas as pd

# The unused 'os' and 'datetime' imports have been removed to fix the linter error.

from backtester.core import run_crossover_backtest

@pytest.fixture
def setup_dummy_database(tmp_path):
    """Creates a temporary DuckDB database for testing."""
    db_path = tmp_path / "test_asset_universe.duckdb"
    dummy_candidates = [
        {"symbol": "AAPL", "fit_score": 90},
        {"symbol": "GOOG", "fit_score": 85},
        {"symbol": "MSFT", "fit_score": 88},
    ]
    df = pd.DataFrame(dummy_candidates)
    
    con = duckdb.connect(database=str(db_path), read_only=False)
    
    con.register('candidates_df_view', df)
    con.execute("CREATE OR REPLACE TABLE candidates AS SELECT * FROM candidates_df_view")
    
    con.close()
    
    return str(db_path)

def test_run_crossover_backtest(setup_dummy_database, capsys, monkeypatch):
    """
    Tests that the run_crossover_backtest function executes without errors
    and prints a performance summary.
    """
    # Use monkeypatch to temporarily change the DB_FILE variable
    monkeypatch.setattr('backtester.core.DB_FILE', setup_dummy_database)
    
    # Run a fast backtest with small windows to speed up the test
    run_crossover_backtest(short_window=10, long_window=20, start_date="2023-01-01", end_date="2023-06-30")

    # Check that the function printed the expected output to the console
    captured = capsys.readouterr()
    assert "--- Performance Summary for 10/20 Strategy" in captured.out
    assert "Total Return [%]" in captured.out
    assert "Error" not in captured.out

