"""Load NGFS scenario CSVs and interpolate to quarterly frequency."""
from __future__ import annotations

import glob
from pathlib import Path
from typing import Dict

import pandas as pd


def parse_ngfs(pattern: str) -> Dict[str, pd.DataFrame]:
    data: Dict[str, pd.DataFrame] = {}
    for path in glob.glob(pattern):
        name = Path(path).stem
        df = pd.read_csv(path)
        if "Year" in df.columns:
            df = df.set_index("Year")
        df.index = pd.PeriodIndex(df.index.astype(int), freq="A")
        df_q = df.resample("Q").interpolate(method="spline", order=3)
        data[name] = df_q
    return data
