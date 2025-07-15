import os
from pathlib import Path
import pandas as pd
import polars as pl
import tempfile
import shutil
from typing import Optional

FEATURE_STORE_ROOT = Path(os.environ.get("FEATURE_STORE_ROOT", "./feature_store"))


def save(df: pd.DataFrame, table_name: str, as_of_ts: str) -> None:
    """Save a DataFrame to partitioned Parquet files.

    Parameters
    ----------
    df : pd.DataFrame
        Data to store.
    table_name : str
        Name of the table folder.
    as_of_ts : str
        Partition timestamp in ``YYYY-MM-DD`` format.
    """
    table_path = FEATURE_STORE_ROOT / table_name
    table_path.mkdir(parents=True, exist_ok=True)
    target = table_path / f"as_of_ts={as_of_ts}"
    tmp_dir = Path(tempfile.mkdtemp(dir=table_path))
    tmp_file = tmp_dir / "data.parquet"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(tmp_file, index=False)
    if target.exists():
        shutil.rmtree(target)
    tmp_dir.rename(target)


def load(table_name: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> pl.LazyFrame:
    """Load data as a Polars ``LazyFrame``.

    Parameters
    ----------
    table_name : str
        Table to load.
    date_from : str, optional
        Start partition ``YYYY-MM-DD``.
    date_to : str, optional
        End partition ``YYYY-MM-DD``.
    """
    table_path = FEATURE_STORE_ROOT / table_name
    if not table_path.exists():
        return pl.LazyFrame()
    parts = []
    for p in table_path.glob("as_of_ts=*"):
        if not p.is_dir():
            continue
        date_str = p.name.split("=")[1]
        if date_from and date_str < date_from:
            continue
        if date_to and date_str > date_to:
            continue
        parts.append(str(p / "*.parquet"))
    if not parts:
        return pl.LazyFrame()
    return pl.scan_parquet(parts)
