# In: tests/test_pipeline.py

import os
import duckdb
import pandas as pd
import pytest
from universe_scouter.storage import save_candidates, DATA_LAKE_PATH
from datetime import datetime

# This pytest fixture now cleans up *before and after* the test runs.
@pytest.fixture
def cleanup_files():
    """A fixture to ensure no old test files exist before or after a test."""
    # Setup code (runs before the test)
    db_file = 'asset_universe.duckdb'
    if os.path.exists(db_file):
        os.remove(db_file)
    
    yield # This is where the test itself will run
    
    # Teardown code (runs after the test is complete)
    if os.path.exists(db_file):
        os.remove(db_file)
    
    today_str = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.join(DATA_LAKE_PATH, today_str)
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith('.parquet'):
                os.remove(os.path.join(output_dir, f))
        if not os.listdir(output_dir): # Only remove if empty
            os.rmdir(output_dir)


def test_save_candidates(cleanup_files):
    """
    Tests that the save_candidates function correctly creates a Parquet file
    and inserts records into the DuckDB database.
    """
    # 1. Arrange: Create sample data to save
    sample_candidates = [
        {
            "symbol": "NVDA", "fit_score": 95, "rationale": "['AI leader']", 
            "predictability_score_rmse": 0.05, "recorded_at": datetime.now()
        },
        {
            "symbol": "TSLA", "fit_score": 75, "rationale": "['EV market']", 
            "predictability_score_rmse": 0.15, "recorded_at": datetime.now()
        }
    ]

    # 2. Act: Call the function we want to test
    save_candidates(sample_candidates)

    # 3. Assert: Check that the files and data were created correctly

    # Assert that the Parquet file was created
    today_str = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.join(DATA_LAKE_PATH, today_str)
    assert os.path.exists(output_dir), "Parquet output directory was not created."
    
    parquet_files = [f for f in os.listdir(output_dir) if f.endswith('.parquet')]
    assert len(parquet_files) >= 1, "Parquet file was not created in the output directory."

    # Assert that the DuckDB was created and has the correct data
    db_file = 'asset_universe.duckdb'
    assert os.path.exists(db_file), "DuckDB file was not created."

    con = duckdb.connect(database=db_file, read_only=True)
    count = con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    con.close()
    
    assert count == 2, "The wrong number of records were inserted into DuckDB."

