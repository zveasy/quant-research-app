from __future__ import annotations

import os
from datetime import date


import duckdb
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

DB_PATH = os.getenv("PERF_DB", "asset_universe.duckdb")
SECRET = os.getenv("JWT_SECRET", "secret")

router = APIRouter()
security = HTTPBearer()


def _auth(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid token") from e


@router.get("/v1/perf")
def perf(from_: date, to: date, class_: str = "equity", creds: HTTPAuthorizationCredentials = Depends(security)):
    _auth(creds)
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(
        "SELECT date, return FROM perf WHERE class = ? AND date BETWEEN ? AND ?",
        [class_, from_, to],
    ).fetch_df()
    con.close()
    return df.to_dict(orient="records")
