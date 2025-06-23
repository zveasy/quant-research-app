# In: alt_data/trends.py

import pandas as pd
from pytrends.request import TrendReq
import time

def get_google_trends_score(keyword: str, timeframe: str = 'today 3-m') -> float:
    """
    Fetches Google Trends data for a keyword and calculates a simple
    momentum score (average interest over the last month vs. the prior two).

    Args:
        keyword (str): The search term (e.g., a stock symbol).
        timeframe (str): The time period to analyze (e.g., 'today 3-m').

    Returns:
        float: The trend score, or 0.0 if data is unavailable.
    """
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
        
        # Get interest over time data
        interest_df = pytrends.interest_over_time()

        if interest_df.empty:
            return 0.0

        # Calculate the score: avg of last 30 days vs. avg of prior period
        last_30_days = interest_df[keyword].iloc[-30:].mean()
        prior_period = interest_df[keyword].iloc[:-30].mean()
        
        # Avoid division by zero
        if prior_period == 0:
            return 0.0
        
        score = (last_30_days / prior_period) - 1.0
        
        # Google Trends may rate limit, so we add a small sleep
        time.sleep(1) 

        return score
        
    except Exception as e:
        # Often returns a 429 error if hit too fast.
        # print(f"Could not fetch Google Trends for {keyword}: {e}")
        return 0.0

# --- To test this function directly ---
if __name__ == '__main__':
    # Test with a high-interest tech stock and a more stable company
    tsla_keyword = "TSLA"
    ko_keyword = "KO" # Coca-Cola

    tsla_trend = get_google_trends_score(tsla_keyword)
    ko_trend = get_google_trends_score(ko_keyword)

    print(f"--- Alternative Data: Google Trends Score ---")
    print(f"3-Month Trend Score for '{tsla_keyword}': {tsla_trend:.2%}")
    print(f"3-Month Trend Score for '{ko_keyword}': {ko_trend:.2%}")