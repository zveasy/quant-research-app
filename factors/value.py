# In: factors/value.py

import yfinance as yf
import numpy as np


def get_price_to_book(symbol: str) -> float:
    """
    Fetches the Price-to-Book (P/B) ratio for a given stock symbol.

    P/B is a classic value factor. A lower P/B can indicate an undervalued stock.

    Args:
        symbol (str): The stock ticker.

    Returns:
        float: The P/B ratio, or np.nan if it's not available.
    """
    try:
        stock_info = yf.Ticker(symbol).info
        pb_ratio = stock_info.get("priceToBook")

        if pb_ratio:
            return float(pb_ratio)
        else:
            # Return NaN if the value doesn't exist for this stock
            return np.nan
    except Exception:
        # Return NaN on any error (e.g., network issue, invalid symbol)
        return np.nan


# --- To test this function directly ---
if __name__ == "__main__":
    # Test with a well-known value stock (a bank) and a growth stock
    jpm_symbol = "JPM"
    tsla_symbol = "TSLA"

    jpm_pb = get_price_to_book(jpm_symbol)
    tsla_pb = get_price_to_book(tsla_symbol)

    print("--- Value Factor: Price-to-Book Ratio ---")
    print(f"P/B for {jpm_symbol}: {jpm_pb:.2f}")
    print(f"P/B for {tsla_symbol}: {tsla_pb:.2f}")
