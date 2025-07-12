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
from alt_data.trends import get_google_trends_score
from factors.fed_rates import get_fed_funds_rate, get_fed_funds_rate_change
from universe_scouter.explorers import EquityExplorer
from universe_scouter.currency_explorer import get_assets as get_currency_assets
from universe_scouter.carbon_credit_explorer import (
    get_assets as get_carbon_credit_assets,
)
from universe_scouter.green_bond_explorer import (
    get_assets as get_green_bond_assets,
)
from universe_scouter.supplier_explorer import get_suppliers

# Read the database path from the environment with a sensible default
DB_FILE = os.getenv("DB_PATH", "./asset_universe.duckdb")


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

    # Ensure local modules are discoverable for imports and tests
    import sys
    sys.path.append(os.path.abspath("."))

    explorer = EquityExplorer()
    equity_df = explorer.get_top_gainers(limit=25)
    equity_df["asset_class"] = "equity"

    currency_df = get_currency_assets()
    currency_df["asset_class"] = "currency"

    carbon_df = get_carbon_credit_assets()
    carbon_df["asset_class"] = "carbon_credit"

    green_df = get_green_bond_assets()
    green_df["asset_class"] = "green_bond"

    # New: include suppliers of major tech companies for a broader search
    supplier_df = get_suppliers(["NVDA", "AAPL"])
    supplier_df["asset_class"] = "supplier"

    discovery_df = pd.concat(
        [equity_df, currency_df, carbon_df, green_df, supplier_df], ignore_index=True
    )
    discovered_assets = discovery_df.to_dict("records")

    # Fetch macro factors once
    fed_rate = get_fed_funds_rate()
    fed_change = get_fed_funds_rate_change()

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
        if pd.notna(fed_rate):
            print(f"   - Fed Funds Rate: {fed_rate:.2f}%")
        if pd.notna(fed_change):
            print(f"   - 30d Rate Change: {fed_change:.2f}")
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
            asset["fed_funds_rate"] = fed_rate
            asset["fed_funds_rate_change"] = fed_change

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
