# In: create_db.py

import pandas as pd
import duckdb
import os
from datetime import datetime
import numpy as np
from universe_scouter.ai_agent import get_ai_fit_score
from universe_scouter.enrichers import get_predictability_score
from factors.value import get_price_to_book
from factors.momentum import get_12m_momentum
from factors.quality import get_debt_to_equity, get_return_on_equity
from factors.volatility import get_annualized_volatility
from alt_data.trends import get_google_trends_score  # <--- NEW IMPORT

# Set your project root directory (not the DB file itself)
PROJECT_ROOT = "/Users/zakariyaveasy/Desktop/ZKJ/quant-research-app"
DB_FILE = os.path.join(PROJECT_ROOT, "asset_universe.duckdb")


def save_candidates_to_db(candidates: list[dict]):
    """Saves the final candidate data to DuckDB, replacing the old table."""
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
    print(
        f"   - Starting with {len(discovered_assets)} assets: {[a['symbol'] for a in discovered_assets]}"
    )

    all_candidates = []
    for asset in discovered_assets:
        print(f"\n--- Processing {asset['symbol']} ---")

        # --- Call all the factor functions ---
        predict_score = get_predictability_score(asset["symbol"])
        pb_ratio = get_price_to_book(asset["symbol"])
        momentum_12m = get_12m_momentum(asset["symbol"])
        de_ratio = get_debt_to_equity(asset["symbol"])
        roe = get_return_on_equity(asset["symbol"])
        ann_vol = get_annualized_volatility(asset["symbol"])

        # --- THIS IS THE NEW STEP ---
        # Enrich with Alternative Data (Google Trends)
        trends_score = get_google_trends_score(asset["symbol"])
        if pd.notna(trends_score):
            print(f"   - Google Trends Score for {asset['symbol']}: {trends_score:.2%}")
        else:
            print(f"   - Google Trends Score for {asset['symbol']}: Not Available")
        # ----------------------------

        if predict_score is not None and np.isfinite(predict_score):
            # Add all factors to the asset data package
            asset["predictability_score_rmse"] = predict_score
            asset["price_to_book"] = pb_ratio
            asset["momentum_12m"] = momentum_12m
            asset["debt_to_equity"] = de_ratio
            asset["return_on_equity"] = roe
            asset["annualized_volatility"] = ann_vol
            asset["google_trends_score"] = trends_score  # Add the new trends score

            # Get the AI score and add it to the final record
            ai_result = get_ai_fit_score(asset["symbol"], asset, dev_mode=True)
            full_record = {**asset, **ai_result}
            full_record["recorded_at"] = datetime.now()
            all_candidates.append(full_record)
        else:
            print(
                f"   - FAILED to get a valid predictability score for {asset['symbol']}. Skipping this asset."
            )

    save_candidates_to_db(all_candidates)
    print("\n✅ Pipeline finished.")
