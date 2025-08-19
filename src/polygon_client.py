"""Client for interacting with the Polygon.io API."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import requests
from scipy import stats

from .config import get_settings


class PolygonClient:
    """Lightweight client for the Polygon.io REST API."""

    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: str | None = None, session: requests.Session | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.polygon_api_key
        self.session = session or requests.Session()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        params = params or {}
        params["apiKey"] = self.api_key
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_aggregates_df(
        self, ticker: str, multiplier: int, timespan: str, from_date: str, to_date: str
    ) -> pd.DataFrame:
        """Fetch aggregate bars for a ticker and return a DataFrame with z-scores.

        Parameters
        ----------
        ticker:
            Equity ticker symbol (e.g., ``"AAPL"``).
        multiplier:
            Size of the timespan multiplier.
        timespan:
            Timespan of the aggregate window (e.g., ``"day"``).
        from_date, to_date:
            ISO-8601 date strings representing the query interval.
        """
        path = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        data = self._get(path)
        results = data.get("results", [])
        df = pd.DataFrame(results)
        if not df.empty and "c" in df:
            # Use numpy and scipy to compute a z-score of log closes
            df["zscore_close"] = stats.zscore(np.log(df["c"].astype(float)))
        return df
