import pandas as pd
from openbb import obb

class EquityExplorer:
    """
    Discovers tradable equity assets using the OpenBB Hub.
    """
    def get_top_gainers(self, limit: int = 250) -> pd.DataFrame:
        """
        Fetches a list of the top-gaining US equities.
        NOTE: The 'actives' function was deprecated, so we use 'gainers' instead.
        """
        print(f"Fetching up to {limit} top gainer equity symbols from OpenBB...")
        try:
            # CORRECTED: Use the .gainers() function which is available.
            top_gainers = obb.equity.discovery.gainers(limit=limit).to_df()
            
            if 'symbol' in top_gainers.columns and 'name' in top_gainers.columns:
                print(f"Successfully fetched {len(top_gainers)} symbols.")
                return top_gainers[['symbol', 'name']].head(limit)
            else:
                print("Error: 'symbol' or 'name' column not found in the data.")
                return pd.DataFrame()

        except Exception as e:
            print(f"An error occurred while fetching data from OpenBB: {e}")
            return pd.DataFrame()

# Example of how to run it
if __name__ == '__main__':
    explorer = EquityExplorer()
    top_stocks = explorer.get_top_gainers(limit=10)
    print("\nTop 10 Top Gaining Stocks:")
    print(top_stocks)