# In: factors/fx_carry.py
"""Functions to compute FX carry metrics."""

import numpy as np
from data_prep.yfinance_utils import yf_download_retry

# Mapping from currency codes to FRED tickers for short-term interest rates
# We use 3-month interbank or treasury rates where available.
CURRENCY_TO_FRED_TICKER = {
    "USD": "DGS3MO",  # 3-Month Treasury Bill: Secondary Market Rate
    "EUR": "EUR3MTD156N",  # Euro Area 3-Month interbank rate
    "JPY": "IR3TIB01JPM156N",  # Japan 3-Month interbank rate
    "GBP": "IR3TIB01GBM156N",  # U.K. 3-Month interbank rate
    "AUD": "IR3TIB01AUM156N",  # Australia 3-Month interbank rate
}


def get_fx_carry(base_currency: str, quote_currency: str) -> float:
    """Calculate the FX carry for a currency pair.

    The carry is defined here as the short‑term interest rate differential
    between the base currency you are long and the funding (quote) currency
    you are short.

    Args:
        base_currency: ISO code of the currency you are long (e.g. ``"EUR"``).
        quote_currency: ISO code of the currency you are short (e.g. ``"USD"``).

    Returns:
        float: Interest rate differential ``base - quote`` or ``np.nan`` if
        data cannot be retrieved.
    """
    try:
        base_ticker = CURRENCY_TO_FRED_TICKER[base_currency.upper()]
        quote_ticker = CURRENCY_TO_FRED_TICKER[quote_currency.upper()]
    except KeyError:
        return np.nan

    try:
        base_data = yf_download_retry(base_ticker, period="5d")
        quote_data = yf_download_retry(quote_ticker, period="5d")

        if base_data.empty or quote_data.empty:
            return np.nan

        base_rate = base_data["Close"].dropna().iloc[-1]
        quote_rate = quote_data["Close"].dropna().iloc[-1]

        return float(base_rate - quote_rate)
    except Exception:
        return np.nan


# --- To test this function directly ---
if __name__ == "__main__":
    print("EUR/USD carry:", get_fx_carry("EUR", "USD"))
