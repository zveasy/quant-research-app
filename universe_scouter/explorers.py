import pandas as pd
from openbb import obb

class EquityExplorer:
    """
    Discovers tradable equity assets using the OpenBB Hub.
    """
    def get_active_equities(self, limit: int = 250) -> pd.DataFrame:
        """
        Fetches a list of the most active US equities.
        """
        print(f"Fetching up to {limit} active equity symbols from OpenBB...")
        try:
            # Fetches the most active stocks
            active_stocks = obb.equity.discovery.actives(limit=limit).to_df()
            
            if 'symbol' in active_stocks.columns and 'name' in active_stocks.columns:
                print(f"Successfully fetched {len(active_stocks)} symbols.")
                return active_stocks[['symbol', 'name']].head(limit)
            else:
                print("Error: 'symbol' or 'name' column not found.")
                return pd.DataFrame()

        except Exception as e:
            print(f"An error occurred while fetching data from OpenBB: {e}")
            return pd.DataFrame()

# Example of how to run it
if __name__ == '__main__':
    explorer = EquityExplorer()
    top_stocks = explorer.get_active_equities(limit=10)
    print("\nTop 10 Most Active Stocks:")
    print(top_stocks)