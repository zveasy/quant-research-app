# In: factors/momentum.py

import yfinance as yf
import numpy as np
import pandas as pd


def compute_momentum(df: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """Compute cross-sectional 12-1 month momentum.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame of close prices indexed by date where each column is a symbol.
    lookback : int, default ``252``
        Look-back window in trading days.

    Returns
    -------
    pandas.DataFrame
        Tidy DataFrame with columns ``date``, ``symbol`` and ``momentum_z``.

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range('2020-01-01', periods=40)
    >>> prices = pd.DataFrame({'AAA': np.arange(40),
    ...                       'BBB': np.linspace(10, 20, 40)}, index=dates)
    >>> res = compute_momentum(prices, lookback=5)
    >>> set(res.columns)
    {'date', 'symbol', 'momentum_z'}
    """

    if isinstance(df.columns, pd.MultiIndex):
        col_levels = df.columns.get_level_values
        if "close" in col_levels(0):
            close = df.xs("close", level=0, axis=1)
        elif "close" in col_levels(-1):
            close = df.xs("close", level=-1, axis=1)
        else:
            raise KeyError("'close' column not found")
    else:
        close = df

    skip = 21
    look = lookback + skip
    returns = close.shift(skip) / close.shift(look) - 1
    returns = returns.dropna(how="all")

    ranks = returns.rank(axis=1, method="average")
    mean = ranks.mean(axis=1)
    std = ranks.std(axis=1, ddof=0)
    zscores = ranks.sub(mean, axis=0).div(std, axis=0)

    result = (
        zscores.stack()
        .rename("momentum_z")
        .reset_index()
        .rename(columns={"level_0": "date", "level_1": "symbol"})
        .dropna()
    )

    return result


def get_12m_momentum(symbol: str) -> float:
    """
    Calculates the 12-month price momentum for a given stock symbol.

    Momentum is the total return over the last year. A higher value
    indicates stronger positive momentum.

    Args:
        symbol (str): The stock ticker.

    Returns:
        float: The 12-month return, or np.nan if it's not available.
    """
    try:
        # Download roughly one year of data
        stock_data = yf.download(symbol, period="1y", progress=False, auto_adjust=True)

        if len(stock_data) < 250:  # Ensure we have enough data for a year
            return np.nan

        # Get the first and last available closing prices
        start_price = stock_data["Close"].iloc[0]
        end_price = stock_data["Close"].iloc[-1]

        # Calculate the percentage return
        momentum = (end_price / start_price) - 1.0

        # --- THIS IS THE FIX ---
        # Use .item() to extract the single float value and remove the warning.
        return momentum.item()

    except Exception:
        # Return NaN on any error
        return np.nan


# --- To test this function directly ---
if __name__ == "__main__":
    # Test with a stock known for recent momentum
    nvda_symbol = "NVDA"
    # And one that might be less so
    vz_symbol = "VZ"

    nvda_mom = get_12m_momentum(nvda_symbol)
    vz_mom = get_12m_momentum(vz_symbol)

    print("--- Momentum Factor: 12-Month Return ---")

    # Check if the result is a valid number before trying to format it
    if pd.notna(nvda_mom):
        print(f"Momentum for {nvda_symbol}: {nvda_mom:.2%}")
    else:
        print(f"Momentum for {nvda_symbol}: Not Available")

    if pd.notna(vz_mom):
        print(f"Momentum for {vz_symbol}: {vz_mom:.2%}")
    else:
        print(f"Momentum for {vz_symbol}: Not Available")
