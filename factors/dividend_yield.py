# In: factors/dividend_yield.py
"""Factor for fetching a stock's dividend yield."""

import time
import yfinance as yf
import numpy as np


def get_dividend_yield(symbol: str, retries: int = 3, delay: float = 1.0) -> float:
    """Return trailing 12-month dividend yield or ``np.nan`` if unavailable."""
    for _ in range(retries):
        try:
            info = yf.Ticker(symbol).info
            value = info.get("dividendYield")
            if value is None:
                return np.nan
            return float(value)
        except Exception:
            time.sleep(delay)
    return np.nan


if __name__ == "__main__":
    print("Dividend Yield for AAPL:", get_dividend_yield("AAPL"))
