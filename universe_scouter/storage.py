# In: universe_scouter/storage.py

import pandas as pd
import duckdb
import os
from datetime import datetime

DATA_LAKE_PATH = "asset_candidates"
os.makedirs(DATA_LAKE_PATH, exist_ok=True)


def save_candidates(candidates: list[dict]):
    if not candidates:
        print("No candidates to save.")
        return

    df = pd.DataFrame(candidates)

    def _pandas_to_duck_type(dtype: pd.api.extensions.ExtensionDtype) -> str:
        if pd.api.types.is_float_dtype(dtype):
            return "DOUBLE"
        if pd.api.types.is_integer_dtype(dtype):
            return "BIGINT"
        if pd.api.types.is_bool_dtype(dtype):
            return "BOOLEAN"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "TIMESTAMP"
        return "VARCHAR"

    # --- Save Parquet ---
    today_str = datetime.now().strftime("%Y%m%d")
    output_dir = os.path.join(DATA_LAKE_PATH, today_str)
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%H%M%S")
    file_path = os.path.join(output_dir, f"candidates_{timestamp_str}.parquet")
    try:
        df.to_parquet(file_path, index=False)
        print(f"✅ Successfully saved {len(df)} candidates to {file_path}")
    except Exception as e:
        print(f"❌ Failed to write Parquet file: {e}")

    # --- Save to DuckDB while preserving existing data ---
    con = duckdb.connect(database="asset_universe.duckdb", read_only=False)
    con.register("new_candidates", df)

    table_exists = bool(
        con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='candidates'"
        ).fetchone()[0]
    )

    if not table_exists:
        con.execute("CREATE TABLE candidates AS SELECT * FROM new_candidates LIMIT 0")

    existing_cols = [row[1] for row in con.execute("PRAGMA table_info('candidates')").fetchall()]

    for col, dtype in df.dtypes.items():
        if col not in existing_cols:
            duck_type = _pandas_to_duck_type(dtype)
            con.execute(f"ALTER TABLE candidates ADD COLUMN {col} {duck_type}")
            existing_cols.append(col)

    for col in existing_cols:
        if col not in df.columns:
            df[col] = pd.NA

    con.register("new_candidates", df)
    cols = ", ".join(df.columns)
    con.execute(f"INSERT INTO candidates ({cols}) SELECT {cols} FROM new_candidates")
    con.close()
    print(f"✅ Inserted {len(df)} records into 'candidates' table in DuckDB.")
