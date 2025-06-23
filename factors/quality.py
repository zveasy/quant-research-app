# In: factors/quality.py

import yfinance as yf
import numpy as np
import pandas as pd

def get_debt_to_equity(symbol: str) -> float:
    """
    Fetches the Debt-to-Equity (D/E) ratio for a given stock symbol.

    D/E is a quality factor that measures a company's financial leverage.
    A lower D/E ratio is generally considered better.

    Args:
        symbol (str): The stock ticker.

    Returns:
        float: The D/E ratio, or np.nan if it's not available.
    """
    try:
        # Get detailed company information
        stock_info = yf.Ticker(symbol).info
        
        # The key for Debt-to-Equity in yfinance is 'debtToEquity'
        de_ratio = stock_info.get('debtToEquity')

        if de_ratio is not None:
            return float(de_ratio)
        else:
            return np.nan
    except Exception:
        # Return NaN on any error
        return np.nan

# --- To test this function directly ---
if __name__ == '__main__':
    # Test with a capital-intensive company and a tech company
    ford_symbol = "F"
    apple_symbol = "AAPL"

    ford_de = get_debt_to_equity(ford_symbol)
    apple_de = get_debt_to_equity(apple_symbol)

    print(f"--- Quality Factor: Debt-to-Equity Ratio ---")

    if pd.notna(ford_de):
        print(f"Debt-to-Equity for {ford_symbol}: {ford_de:.2f}")
    else:
        print(f"Debt-to-Equity for {ford_symbol}: Not Available")

    if pd.notna(apple_de):
        print(f"Debt-to-Equity for {apple_symbol}: {apple_de:.2f}")
    else:
        print(f"Debt-to-Equity for {apple_symbol}: Not Available")