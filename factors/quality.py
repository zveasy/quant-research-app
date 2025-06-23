# In: factors/quality.py

import yfinance as yf
import numpy as np
import pandas as pd

def get_debt_to_equity(symbol: str) -> float:
    """
    Fetches the Debt-to-Equity (D/E) ratio for a given stock symbol.
    """
    try:
        stock_info = yf.Ticker(symbol).info
        de_ratio = stock_info.get('debtToEquity')

        if de_ratio is not None:
            return float(de_ratio)
        else:
            return np.nan
    except Exception:
        return np.nan

def get_return_on_equity(symbol: str) -> float:
    """
    Fetches the Return on Equity (ROE) for a given stock symbol.
    """
    try:
        stock_info = yf.Ticker(symbol).info
        roe = stock_info.get('returnOnEquity')

        if roe is not None:
            return float(roe)
        else:
            return np.nan
    except Exception:
        return np.nan

# --- To test BOTH functions in this file ---
if __name__ == '__main__':
    test_symbol = "GS" # Goldman Sachs, a financial company
    test_symbol_2 = "AAPL" # Apple, a tech company

    print(f"--- Quality Factors for {test_symbol} & {test_symbol_2} ---")

    # Test Debt-to-Equity for GS
    de_ratio = get_debt_to_equity(test_symbol)
    if pd.notna(de_ratio):
        print(f"Debt-to-Equity for {test_symbol}: {de_ratio:.2f}")
    else:
        print(f"Debt-to-Equity for {test_symbol}: Not Available")

    # Test Return on Equity for GS
    roe = get_return_on_equity(test_symbol)
    if pd.notna(roe):
        print(f"Return on Equity for {test_symbol}: {roe:.2%}")
    else:
        print(f"Return on Equity for {test_symbol}: Not Available")
        
    print("---")

    # Test Debt-to-Equity for AAPL
    de_ratio_2 = get_debt_to_equity(test_symbol_2)
    if pd.notna(de_ratio_2):
        print(f"Debt-to-Equity for {test_symbol_2}: {de_ratio_2:.2f}")
    else:
        print(f"Debt-to-Equity for {test_symbol_2}: Not Available")
        
    # Test Return on Equity for AAPL
    roe_2 = get_return_on_equity(test_symbol_2)
    if pd.notna(roe_2):
        print(f"Return on Equity for {test_symbol_2}: {roe_2:.2%}")
    else:
        print(f"Return on Equity for {test_symbol_2}: Not Available")