"""Lambda to monitor cross-region data transfer costs."""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Dict

import boto3
import requests

DAILY_LIMIT = float(os.environ.get("DAILY_LIMIT", "0"))
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")


def fetch_transfer_usage() -> Dict[str, float]:
    ce = boto3.client("ce")
    today = dt.date.today()
    start = today - dt.timedelta(days=1)
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start.isoformat(), "End": today.isoformat()},
        Granularity="DAILY",
        Metrics=["UsageQuantity"],
        Filter={"Dimensions": {"Key": "UsageType", "Values": ["DataTransfer-Out-Bytes"]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}],
    )
    usage: Dict[str, float] = {}
    for group in resp.get("ResultsByTime", [])[0].get("Groups", []):
        region = group["Keys"][0]
        amount = float(group["Metrics"]["UsageQuantity"]["Amount"])
        usage[region] = usage.get(region, 0) + amount
    return usage


def send_alert(message: str) -> None:
    if SLACK_WEBHOOK:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=10)


def lambda_handler(event, context) -> Dict[str, float]:
    usage = fetch_transfer_usage()
    breached = {r: v for r, v in usage.items() if v > DAILY_LIMIT}
    if breached:
        lines = [f"{r}: {v:.2f} bytes" for r, v in breached.items()]
        send_alert("Data transfer exceeded limit:\n" + "\n".join(lines))
    return usage


if __name__ == "__main__":
    print(json.dumps(lambda_handler({}, {}), indent=2))
