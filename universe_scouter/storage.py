# In: universe_scouter/storage.py

import pandas as pd
import duckdb
import os
from datetime import datetime
import json

DATA_LAKE_PATH = "asset_candidates"
os.makedirs(DATA_LAKE_PATH, exist_ok=True)

def save_candidates(candidates: list[dict]):
    if not candidates:
        print("No candidates to save.")
        return

    df = pd.DataFrame(candidates)
    
    # --- Save Parquet ---
    today_str = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.join(DATA_LAKE_PATH, today_str)
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime('%H%M%S')
    file_path = os.path.join(output_dir, f"candidates_{timestamp_str}.parquet")
    df.to_parquet(file_path, index=False)
    print(f"✅ Successfully saved {len(df)} candidates to {file_path}")

    # --- Save to DuckDB (using a more robust method) ---
    con = duckdb.connect(database='asset_universe.duckdb', read_only=False)
    # This command creates a fresh table from the DataFrame every time,
    # which avoids schema mismatch errors.
    con.execute("CREATE OR REPLACE TABLE candidates AS SELECT * FROM df")
    con.close()
    print(f"✅ Replaced 'candidates' table in DuckDB with {len(df)} new records.")