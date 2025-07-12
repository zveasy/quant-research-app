import pandas as pd

# Simple mapping of major companies to some of their key suppliers.
# These names are illustrative and would normally come from a data source.
SUPPLIER_MAP = {
    "NVDA": [
        ("TSM", "Taiwan Semiconductor"),
        ("ASML", "ASML Holding"),
        ("ARM", "Arm Holdings"),
    ],
    "AAPL": [
        ("CRUS", "Cirrus Logic"),
        ("SWKS", "Skyworks Solutions"),
        ("QCOM", "Qualcomm Inc."),
    ],
}


def get_suppliers(companies: list[str]) -> pd.DataFrame:
    """Return a DataFrame of supplier symbols and names for the given companies."""
    rows = []
    for comp in companies:
        for sym, name in SUPPLIER_MAP.get(comp.upper(), []):
            rows.append({"symbol": sym, "name": name})
    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)
