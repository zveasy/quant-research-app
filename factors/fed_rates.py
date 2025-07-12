# In: factors/fed_rates.py
"""Utilities for retrieving Federal Reserve interest rate metrics."""

import numpy as np
import yfinance as yf


def get_fed_funds_rate() -> float:
    """Fetch the latest effective Federal Funds Rate (FRED ticker 'DFF')."""
    try:
        data = yf.download("DFF", period="5d", progress=False)
        if data.empty:
            return np.nan
        return float(data["Close"].dropna().iloc[-1])
    except Exception:
        return np.nan


def get_fed_funds_rate_change(days: int = 30) -> float:
    """Return the change in the effective Fed Funds Rate over the given period."""
    try:
        data = yf.download("DFF", period=f"{days}d", progress=False)
        closes = data["Close"].dropna()
        if len(closes) < 2:
            return np.nan
        return float(closes.iloc[-1] - closes.iloc[0])
    except Exception:
        return np.nan


# --- To test this module directly ---
if __name__ == "__main__":
    rate = get_fed_funds_rate()
    change = get_fed_funds_rate_change()
    print("Fed Funds Rate:", rate)
    print("1M Change:", change)
