import pandas as pd
import numpy as np

def get_returns(df, mode="simple"):
    """
    Calculates returns for a DataFrame of prices.
    mode: "simple" or "log"
    """
    if mode == "simple":
        return df.pct_change().dropna()
    elif mode == "log":
        return np.log(df / df.shift(1)).dropna()
    else:
        raise ValueError("mode must be 'simple' or 'log'")

def get_volatility(df_returns, window=22):
    """
    Calculates rolling annualized volatility.
    Assumes input is returns, not raw prices.
    """
    return df_returns.rolling(window).std() * np.sqrt(252)

def to_freq(df, freq="M"):
    """
    Resamples a DataFrame to a given frequency.
    freq: 'D' = daily, 'W' = weekly, 'M' = monthly, etc.
    """
    return df.resample(freq).last().ffill()
