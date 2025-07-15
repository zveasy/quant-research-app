"""ETL job moving PostHog events from S3 to ClickHouse."""

from __future__ import annotations

import json
import os
from datetime import datetime

import boto3
import clickhouse_connect
import schedule

S3_BUCKET = os.environ.get("POSTHOG_BUCKET", "posthog-events")
CLICKHOUSE_URL = os.environ.get("CLICKHOUSE_URL", "http://localhost:8123")


def load_events():
    s3 = boto3.client("s3")
    click = clickhouse_connect.get_client(url=CLICKHOUSE_URL)
    objs = s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", [])
    for obj in objs:
        body = s3.get_object(Bucket=S3_BUCKET, Key=obj["Key"]) ["Body"].read()
        events = [json.loads(line) for line in body.splitlines()]
        rows = [(e["timestamp"], e["event"], json.dumps(e)) for e in events]
        click.insert("posthog.events", rows, column_names=["timestamp", "event", "raw"])
    click.command("""
        CREATE TABLE IF NOT EXISTS posthog.daily AS
        SELECT toDate(timestamp) AS day, count() AS cnt
        FROM posthog.events GROUP BY day
    """)
    click.command("INSERT INTO posthog.daily SELECT toDate(timestamp), count() FROM posthog.events GROUP BY toDate(timestamp)")


if __name__ == "__main__":
    schedule.every(6).hours.do(load_events)
    load_events()
    while True:
        schedule.run_pending()
