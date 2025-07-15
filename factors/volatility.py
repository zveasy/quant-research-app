# In: factors/volatility.py

from data_prep.yfinance_utils import yf_download_retry
import numpy as np
import pandas as pd


def get_annualized_volatility(symbol: str) -> float:
    """
    Calculates the 1-year annualized volatility (standard deviation
    of daily returns) for a given stock symbol.

    Args:
        symbol (str): The stock ticker.

    Returns:
        float: The annualized volatility, or np.nan if data is insufficient.
    """
    try:
        # Download one year of daily price data with basic retry logic
        stock_data = yf_download_retry(symbol, period="1y", auto_adjust=True)

        if len(stock_data) < 250:
            return np.nan

        # Calculate daily returns
        daily_returns = stock_data["Close"].pct_change().dropna()

        # Calculate the standard deviation of daily returns
        daily_volatility = daily_returns.std()

        # Annualize the volatility (sqrt of 252 trading days)
        annualized_vol = daily_volatility * np.sqrt(252)

        return annualized_vol.item()
    except Exception:
        return np.nan


# --- To test this function directly ---
if __name__ == "__main__":
    # Test with a historically volatile stock and a more stable utility stock
    tsla_symbol = "TSLA"
    duk_symbol = "DUK"  # Duke Energy

    tsla_vol = get_annualized_volatility(tsla_symbol)
    duk_vol = get_annualized_volatility(duk_symbol)

    print("--- Volatility Factor: 1-Year Annualized Volatility ---")

    if pd.notna(tsla_vol):
        print(f"Annualized Volatility for {tsla_symbol}: {tsla_vol:.2%}")
    else:
        print(f"Annualized Volatility for {tsla_symbol}: Not Available")

    if pd.notna(duk_vol):
        print(f"Annualized Volatility for {duk_symbol}: {duk_vol:.2%}")
    else:
        print(f"Annualized Volatility for {duk_symbol}: Not Available")
