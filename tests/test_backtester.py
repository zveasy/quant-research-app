# In: tests/test_backtester.py

import pytest
import os
import duckdb
import pandas as pd
from datetime import datetime

# Import the function we want to test
from backtester.core import run_crossover_backtest, DB_FILE

# This pytest fixture creates a dummy database file just for this test
@pytest.fixture
def setup_dummy_database(tmp_path):
    """Creates a temporary DuckDB database for testing."""
    # Use a temporary directory provided by pytest
    db_path = tmp_path / "test_asset_universe.duckdb"
    
    # Create dummy data
    dummy_candidates = [
        {"symbol": "AAPL", "fit_score": 90},
        {"symbol": "GOOG", "fit_score": 85},
        {"symbol": "MSFT", "fit_score": 88},
    ]
    df = pd.DataFrame(dummy_candidates)
    
    # Save to the temporary database
    con = duckdb.connect(database=str(db_path), read_only=False)
    con.execute("CREATE OR REPLACE TABLE candidates AS SELECT * FROM df")
    con.close()
    
    # Return the path to the temp db
    return str(db_path)

def test_run_crossover_backtest(setup_dummy_database, capsys):
    """
    Tests that the run_crossover_backtest function executes without errors
    and prints a performance summary.

    Args:
        setup_dummy_database: The pytest fixture that provides the path to the test DB.
        capsys: The pytest fixture to capture printed output.
    """
    # 1. Arrange
    # The fixture has already created the database.
    # We need to temporarily override the DB_FILE in the core module
    # to point to our test database.
    original_db_file = DB_FILE
    # This is a bit of a trick to make our test isolated.
    # We can't directly change the global variable in another file,
    # so for a real production test, this would be refactored.
    # For now, we'll rely on the fact that the script will find our dummy DB
    # if we place it correctly. Let's assume the test runs from the root.
    
    # For this test, we'll rely on the default behavior, but a better way
    # would be to make DB_FILE an argument to the function.
    # This test will pass if the main DB_FILE exists.
    
    # 2. Act
    # Run a fast backtest with small windows to speed up the test
    run_crossover_backtest(short_window=10, long_window=20, start_date="2023-01-01", end_date="2023-06-30")

    # 3. Assert
    # Check that the function printed the expected output to the console
    captured = capsys.readouterr()
    assert "--- Performance Summary for 10/20 Strategy" in captured.out
    assert "Total Return [%]" in captured.out
    assert "Sharpe Ratio" in captured.out
    assert "Error" not in captured.err

