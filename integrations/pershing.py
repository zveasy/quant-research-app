"""Adapter for Pershing NetX to fetch positions and trades."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

log = logging.getLogger(__name__)


class PershingAdapter:
    """Simple wrapper around Pershing NetX REST API."""

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=4))
    def _get(self, path: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def positions(self) -> List[Dict[str, Any]]:
        data = self._get("/positions")
        return [self._map(record) for record in data]

    def trades(self) -> List[Dict[str, Any]]:
        data = self._get("/trades")
        return [self._map(record) for record in data]

    @staticmethod
    def _map(record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "account_id": record.get("accountId"),
            "symbol": record.get("symbol"),
            "qty": float(record.get("quantity", 0)),
            "price": float(record.get("price", 0)),
            "trade_ts": record.get("tradeDate") or record.get("timestamp"),
        }


def fetch_all(base_url: str, token: str) -> Dict[str, List[Dict[str, Any]]]:
    api = PershingAdapter(base_url, token)
    return {"positions": api.positions(), "trades": api.trades()}
