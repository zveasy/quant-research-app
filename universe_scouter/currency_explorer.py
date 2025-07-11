import pandas as pd


def get_assets(limit: int = 20) -> pd.DataFrame:
    """Return a DataFrame of common currency symbols and names.

    This function attempts to use the optional OpenBB API if it is
    installed. When OpenBB is unavailable the function falls back to a
    small static list so that unit tests can run without network access.
    """
    try:
        from openbb import obb  # type: ignore

        df = obb.forex.discovery.currencies().to_df()
        if "symbol" in df.columns and "name" in df.columns:
            return df[["symbol", "name"]].head(limit)
    except Exception:
        # In tests or environments without OpenBB we simply return
        # a small set of popular currencies.
        pass

    sample = [
        {"symbol": "USD", "name": "US Dollar"},
        {"symbol": "EUR", "name": "Euro"},
        {"symbol": "JPY", "name": "Japanese Yen"},
        {"symbol": "GBP", "name": "British Pound"},
    ]
    return pd.DataFrame(sample).head(limit)
