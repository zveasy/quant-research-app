# In: backtester/core.py

import duckdb
import yfinance as yf
import vectorbt as vbt
import os

# --- Configuration ---
PROJECT_ROOT = "/Users/joshuaveasy/O and L/jv-quant-research"
DB_FILE = os.path.join(PROJECT_ROOT, "asset_universe.duckdb")
NUM_ASSETS_TO_TEST = 3


def run_crossover_backtest(
    short_window: int, long_window: int, start_date: str = None, end_date: str = None
):
    """
    Loads top assets and backtests a moving average crossover strategy
    with customizable window lengths and optional date ranges for stress testing.

    Args:
        short_window (int): The number of days for the short-term moving average.
        long_window (int): The number of days for the long-term moving average.
        start_date (str, optional): The start date for the backtest (YYYY-MM-DD).
        end_date (str, optional): The end date for the backtest (YYYY-MM-DD).
    """
    test_period = (
        f"{start_date} to {end_date}" if start_date and end_date else "full period"
    )
    print(
        f"\n\n--- Starting Back-test for {short_window}/{long_window} Crossover ({test_period}) ---"
    )

    # 1. Load top assets from the database
    try:
        con = duckdb.connect(database=DB_FILE, read_only=True)
        top_assets_df = con.execute(
            f"SELECT symbol FROM candidates ORDER BY fit_score DESC LIMIT {NUM_ASSETS_TO_TEST}"
        ).fetchdf()
        con.close()
        symbols = top_assets_df["symbol"].tolist()
        print(f"Loaded top {len(symbols)} assets for back-test: {symbols}")
    except Exception as e:
        print(f"❌ Error loading assets from database: {e}")
        return

    # 2. Download historical price data
    # Use the start and end dates if provided, otherwise default to 5 years
    period = "5y" if not start_date else None
    print(f"\nDownloading historical price data ({test_period})...")
    price_data = yf.download(
        symbols, start=start_date, end=end_date, period=period, auto_adjust=True
    )["Close"]
    if price_data.empty:
        print("❌ Could not download price data. Exiting.")
        return

    # 3. Generate trading signals
    print("\nGenerating signals...")
    short_ma = vbt.MA.run(price_data, short_window)
    long_ma = vbt.MA.run(price_data, long_window)
    entries = short_ma.ma_crossed_above(long_ma)
    exits = short_ma.ma_crossed_below(long_ma)

    # 4. Run the back-test
    portfolio = vbt.Portfolio.from_signals(
        price_data,
        entries,
        exits,
        freq="D",
        init_cash=10000,
        fees=0.001,
        slippage=0.001,
    )

    # 5. Print performance summary
    print(
        f"\n--- Performance Summary for {short_window}/{long_window} Strategy ({test_period}) ---"
    )
    print(portfolio.stats())


# --- To run this script directly ---
if __name__ == "__main__":
    # --- Full Period Back-tests ---
    print("--- Running Full Period Simulations ---")
    run_crossover_backtest(short_window=50, long_window=200)
    run_crossover_backtest(short_window=20, long_window=50)

    # --- Stress Test Scenario: COVID-19 Crash ---
    print("\n\n--- Running Stress Test: COVID-19 Crash Scenario ---")
    run_crossover_backtest(
        short_window=20, long_window=50, start_date="2020-02-01", end_date="2020-04-30"
    )
