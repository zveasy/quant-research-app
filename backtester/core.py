# In: backtester/core.py

import duckdb
import yfinance as yf
import vectorbt as vbt
import os
import pandas as pd

# Default symbols for non-equity asset classes used when no database is
# available for them. These are intentionally short lists so unit tests can run
# quickly with patched data.
ASSET_CLASS_SYMBOLS = {
    "crypto": ["BTC-USD", "ETH-USD"],
    "bonds": ["IEF"],
    "forex": ["EURUSD=X"],
}

# --- Configuration ---
# Use environment variable for the database location with a default
DB_FILE = os.getenv("DB_PATH", "./asset_universe.duckdb")
NUM_ASSETS_TO_TEST = 3


def run_crossover_backtest(
    short_window: int,
    long_window: int,
    start_date: str | None = None,
    end_date: str | None = None,
    asset_classes: list[str] | None = None,
):
    """
    Loads top assets and backtests a moving average crossover strategy
    with customizable window lengths and optional date ranges for stress testing.

    Args:
        short_window (int): The number of days for the short-term moving average.
        long_window (int): The number of days for the long-term moving average.
        start_date (str, optional): The start date for the backtest (YYYY-MM-DD).
        end_date (str, optional): The end date for the backtest (YYYY-MM-DD).
        asset_classes (list[str], optional): List of asset classes to include.
            Equities are loaded from the candidates database while other classes
            use built-in symbol mappings. Defaults to ["equity"].
    """
    if asset_classes is None:
        asset_classes = ["equity"]

    test_period = (
        f"{start_date} to {end_date}" if start_date and end_date else "full period"
    )
    print(
        f"\n\n--- Starting Back-test for {short_window}/{long_window} Crossover ({test_period}) ---"
    )

    symbols: list[str] = []

    if "equity" in asset_classes:
        try:
            con = duckdb.connect(database=DB_FILE, read_only=True)
            top_assets_df = con.execute(
                f"SELECT symbol FROM candidates ORDER BY fit_score DESC LIMIT {NUM_ASSETS_TO_TEST}"
            ).fetchdf()
            con.close()
            eq_symbols = top_assets_df["symbol"].tolist()
            symbols.extend(eq_symbols)
            print(f"Loaded top {len(eq_symbols)} equity assets for back-test: {eq_symbols}")
        except Exception as e:
            print(f"❌ Error loading equity assets from database: {e}")
            return

    for cls in asset_classes:
        if cls == "equity":
            continue
        extras = ASSET_CLASS_SYMBOLS.get(cls, [])
        if extras:
            symbols.extend(extras)
            print(f"Added {cls} assets: {extras}")
        else:
            print(f"⚠️ Unknown asset class: {cls}")

    if not symbols:
        print("❌ No symbols to back-test. Exiting.")
        return

    # 2. Download historical price data
    # Use the start and end dates if provided, otherwise default to 5 years
    period = "5y" if not start_date else None
    print(f"\nDownloading historical price data ({test_period})...")
    price_data = yf.download(
        symbols, start=start_date, end=end_date, period=period, auto_adjust=True
    )["Close"]
    if price_data.empty:
        print("⚠️ Yahoo download failed. Falling back to sample data.")
        try:
            sample_path = os.path.join(
                os.path.dirname(__file__), "..", "sample_data", "multi_stock.csv"
            )
            sample_df = pd.read_csv(sample_path, index_col="Date", parse_dates=True)
            cols = [s for s in symbols if s in sample_df.columns]
            if not cols:
                print("❌ No matching symbols in sample data. Exiting.")
                return
            price_data = sample_df[cols]
            if start_date or end_date:
                price_data = price_data.loc[start_date:end_date]
            if price_data.empty:
                date_range = pd.date_range(start=start_date or sample_df.index[0], end=end_date or sample_df.index[-1])
                price_data = pd.DataFrame(100.0, index=date_range, columns=cols)
            else:
                price_data = price_data.ffill()
        except Exception as e:
            print(f"❌ Could not load fallback data: {e}")
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
