# In: factors/bond_duration.py
"""Utility for retrieving bond duration metrics."""

import numpy as np
import yfinance as yf


def get_bond_duration(symbol: str) -> float:
    """Fetch the duration for a bond ETF or instrument.

    This function relies on the ``duration`` field returned by ``yfinance``.
    If the value is missing or data cannot be fetched, ``np.nan`` is returned.

    Args:
        symbol: The bond ticker (e.g. ``"IEF"`` for a Treasury ETF).

    Returns:
        float: Duration in years or ``np.nan`` if unavailable.
    """

    try:
        info = yf.Ticker(symbol).info
        duration = info.get("duration")
        if duration is not None:
            return float(duration)
        return np.nan
    except Exception:
        return np.nan


# --- To test this function directly ---
if __name__ == "__main__":
    print("Duration for IEF:", get_bond_duration("IEF"))
