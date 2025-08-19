"""Tests for the PolygonClient class."""
import pytest
import requests

from src.polygon_client import PolygonClient


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):  # pragma: no cover - stubbed
        return None


def test_aggregates_df(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"results": [{"c": 1.0}, {"c": 2.0}, {"c": 3.0}]}

    session = requests.Session()

    def fake_get(url, params, timeout):
        return DummyResponse(payload)

    monkeypatch.setenv("POLYGON_API_KEY", "test-key")
    monkeypatch.setattr(session, "get", fake_get)
    client = PolygonClient(session=session)

    df = client.get_aggregates_df("AAPL", 1, "day", "2020-01-01", "2020-01-03")
    assert "zscore_close" in df.columns
    assert len(df) == 3
