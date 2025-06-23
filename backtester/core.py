# In: backtester/core.py

import duckdb
import yfinance as yf
import vectorbt as vbt
import os

# --- Configuration ---
# Use the absolute path to ensure the db is found
PROJECT_ROOT = "/Users/joshuaveasy/O and L/jv-quant-research"
DB_FILE = os.path.join(PROJECT_ROOT, "asset_universe.duckdb")
NUM_ASSETS_TO_TEST = 3 # How many top-ranked assets to include in the backtest

def run_simple_backtest():
    """
    Loads the top N assets from the database, downloads their price history,
    and runs a simple buy-and-hold backtest using vectorbt.
    """
    print("--- Starting Simple Back-test ---")

    # 1. Load top N assets from the database
    try:
        con = duckdb.connect(database=DB_FILE, read_only=True)
        top_assets_df = con.execute(f"""
            SELECT symbol 
            FROM candidates 
            ORDER BY fit_score DESC 
            LIMIT {NUM_ASSETS_TO_TEST}
        """).fetchdf()
        con.close()
        
        symbols = top_assets_df['symbol'].tolist()
        print(f"Loaded top {len(symbols)} assets for back-test: {symbols}")

    except Exception as e:
        print(f"❌ Error loading assets from database: {e}")
        print("Please ensure you have run 'python create_db.py' first.")
        return

    # 2. Download historical price data for these assets
    print("\nDownloading historical price data (2 years)...")
    price_data = yf.download(symbols, period="2y", auto_adjust=True)['Close']

    if price_data.empty:
        print("❌ Could not download price data. Exiting.")
        return

    # 3. Run the back-test
    # We will simulate a simple strategy: buy and hold an equal-weighted portfolio
    print("\nRunning equal-weighted buy-and-hold simulation...")
    portfolio = vbt.Portfolio.from_holding(price_data, freq='D', init_cash=10000)
    
    # 4. Print performance summary
    print("\n--- Back-test Performance Summary ---")
    print(portfolio.stats())


# --- To run this script directly ---
if __name__ == "__main__":
    run_simple_backtest()
