import json
from types import SimpleNamespace

import pytest

from alt_data.sec_filings import fetch_latest_filing_text


class DummyResp:
    def __init__(self, text="", json_data=None):
        self.text = text
        self._json = json_data or {}

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


def fake_get(url, headers=None, timeout=10):
    if "company_tickers.json" in url:
        return DummyResp(json_data={"0": {"cik_str": 320193, "ticker": "AAPL"}})
    if "CIK0000320193.json" in url:
        data = {
            "filings": {
                "recent": {
                    "form": ["10-K"],
                    "accessionNumber": ["0000320193-23-000106"],
                    "primaryDocument": ["aapl-20230930.htm"],
                }
            }
        }
        return DummyResp(json_data=data)
    if "aapl-20230930.htm" in url:
        return DummyResp("<html>Filing Text AAPL</html>")
    raise RuntimeError("Unexpected URL")


def test_fetch_latest_filing_text(monkeypatch):
    monkeypatch.setattr("requests.get", fake_get)
    text = fetch_latest_filing_text("AAPL")
    assert "Filing Text AAPL" in text
