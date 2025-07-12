from universe_scouter.supplier_explorer import get_suppliers
import pandas as pd


def test_get_suppliers():
    df = get_suppliers(["NVDA"])
    assert not df.empty
    assert set(["symbol", "name"]).issubset(df.columns)
