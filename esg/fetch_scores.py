from __future__ import annotations

import io
import json
import os
from typing import Iterable, Dict

import backoff
import boto3
import httpx
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

MSCI_URL = "https://api.msci.com/esg/v1/scores/{symbol}"
SASB_URL = "https://api.sasb.org/v1/scores/{symbol}"
S3_BUCKET = os.getenv("ESG_S3_BUCKET", "esg-cache")


@backoff.on_exception(backoff.expo, httpx.HTTPError, max_tries=3)
def _fetch(url: str) -> Dict:
    resp = httpx.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_scores(symbols: Iterable[str], parquet_key: str = "scores.parquet") -> pd.DataFrame:
    s3 = boto3.client("s3")
    records = []
    for sym in symbols:
        msci = _fetch(MSCI_URL.format(symbol=sym))
        sasb = _fetch(SASB_URL.format(symbol=sym))
        raw = {"msci": msci, "sasb": sasb}
        s3.put_object(Bucket=S3_BUCKET, Key=f"raw/{sym}.json", Body=json.dumps(raw).encode())
        records.append(
            {
                "symbol": sym,
                "esg_score": msci.get("esg_score"),
                "carbon_score": sasb.get("carbon_score"),
                "diversity_score": sasb.get("diversity_score"),
            }
        )
    df = pd.DataFrame(records)
    table = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table, buf)
    buf.seek(0)
    s3.put_object(Bucket=S3_BUCKET, Key=parquet_key, Body=buf.read())
    return df
