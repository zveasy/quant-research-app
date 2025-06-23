# In: factors/momentum.py

import yfinance as yf
import numpy as np
import pandas as pd # <-- Add this import

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

        if len(stock_data) < 250: # Ensure we have enough data for a year
            return np.nan

        # Get the first and last available closing prices
        start_price = stock_data['Close'].iloc[0]
        end_price = stock_data['Close'].iloc[-1]

        # Calculate the percentage return
        momentum = (end_price / start_price) - 1.0
        
        # Ensure we return a standard float, not a numpy float or Series item
        return float(momentum)
        
    except Exception:
        # Return NaN on any error
        return np.nan

# --- To test this function directly ---
if __name__ == '__main__':
    # Test with a stock known for recent momentum
    nvda_symbol = "NVDA"
    # And one that might be less so
    vz_symbol = "VZ"

    nvda_mom = get_12m_momentum(nvda_symbol)
    vz_mom = get_12m_momentum(vz_symbol)

    print(f"--- Momentum Factor: 12-Month Return ---")
    
    # --- THIS IS THE FIX ---
    # Check if the result is a valid number before trying to format it
    if pd.notna(nvda_mom):
        print(f"Momentum for {nvda_symbol}: {nvda_mom:.2%}")
    else:
        print(f"Momentum for {nvda_symbol}: Not Available")

    if pd.notna(vz_mom):
        print(f"Momentum for {vz_symbol}: {vz_mom:.2%}")
    else:
        print(f"Momentum for {vz_symbol}: Not Available")
    # -----------------------