import pandas as pd


def get_assets(limit: int = 20) -> pd.DataFrame:
    """Return a DataFrame of green bond issuances.

    If the optional OpenBB package is installed it is queried for data.
    Otherwise a very small sample list is returned.
    """
    try:
        from openbb import obb  # type: ignore

        df = obb.fixedincome.greenbonds.search().to_df()
        if "symbol" in df.columns and "name" in df.columns:
            return df[["symbol", "name"]].head(limit)
    except Exception:
        pass

    sample = [
        {"symbol": "US912810RE75", "name": "US T-Bond Green"},
        {"symbol": "XS1505564893", "name": "KfW Green Bond"},
    ]
    return pd.DataFrame(sample).head(limit)
