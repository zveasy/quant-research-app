import pandas as pd


def get_assets(limit: int = 20) -> pd.DataFrame:
    """Return a DataFrame of carbon credit related assets.

    The OpenBB API is used when available. For environments without the
    dependency a tiny static list is provided so that tests can execute.
    """
    try:
        from openbb import obb  # type: ignore

        df = obb.esg.carbon_credits.search().to_df()
        if "symbol" in df.columns and "name" in df.columns:
            return df[["symbol", "name"]].head(limit)
    except Exception:
        pass

    sample = [
        {"symbol": "EUA", "name": "EU Allowance"},
        {"symbol": "CCA", "name": "California Carbon Allowance"},
    ]
    return pd.DataFrame(sample).head(limit)
