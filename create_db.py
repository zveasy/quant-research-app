# In: create_db.py

import pandas as pd
import duckdb
import os
from datetime import datetime
import json
import numpy as np
from universe_scouter.ai_agent import get_ai_fit_score
from universe_scouter.enrichers import get_predictability_score
from factors.value import get_price_to_book
from factors.momentum import get_12m_momentum
from factors.quality import get_debt_to_equity # <--- NEW IMPORT

# PASTE YOUR FULL PATH FROM THE 'pwd' COMMAND HERE
PROJECT_ROOT = "/Users/joshuaveasy/O and L/jv-quant-research"
DB_FILE = os.path.join(PROJECT_ROOT, "asset_universe.duckdb")

def save_candidates_to_db(candidates: list[dict]):
    print(f"--- Saving data to absolute path: '{DB_FILE}' ---")
    if not candidates:
        print("No candidates to save.")
        return

    df = pd.DataFrame(candidates)
    con = duckdb.connect(database=DB_FILE, read_only=False)
    con.execute("CREATE OR REPLACE TABLE candidates AS SELECT * FROM df")
    con.close()
    if os.path.exists(DB_FILE):
        print(f"✅ SUCCESS: Database file created with {len(df)} records at {DB_FILE}")

if __name__ == "__main__":
    print("🚀 Starting Universe Scout pipeline with REAL enrichers...")

    discovered_assets = [{"symbol": "MSFT"}, {"symbol": "GOOG"}, {"symbol": "JPM"}]
    print(f"   - Starting with {len(discovered_assets)} assets: {[a['symbol'] for a in discovered_assets]}")

    all_candidates = []
    for asset in discovered_assets:
        print(f"\n--- Processing {asset['symbol']} ---")
        
        predict_score = get_predictability_score(asset['symbol'])
        pb_ratio = get_price_to_book(asset['symbol'])
        momentum_12m = get_12m_momentum(asset['symbol'])

        # --- THIS IS THE NEW STEP ---
        # Enrich with Quality Factor (Debt-to-Equity)
        de_ratio = get_debt_to_equity(asset['symbol'])
        if pd.notna(de_ratio):
             print(f"   - Debt-to-Equity for {asset['symbol']}: {de_ratio:.2f}")
        else:
             print(f"   - Debt-to-Equity for {asset['symbol']}: Not Available")
        # ----------------------------

        if predict_score is not None and np.isfinite(predict_score):
            asset['predictability_score_rmse'] = predict_score
            asset['price_to_book'] = pb_ratio
            asset['momentum_12m'] = momentum_12m
            asset['debt_to_equity'] = de_ratio # Add the new quality factor
            
            ai_result = get_ai_fit_score(asset['symbol'], asset, dev_mode=True)
            
            full_record = {**asset, **ai_result}
            full_record['recorded_at'] = datetime.now()
            all_candidates.append(full_record)
        else:
            print(f"   - FAILED to get a valid predictability score for {asset['symbol']}. Skipping this asset.")

    save_candidates_to_db(all_candidates)
    print("\n✅ Pipeline finished.")