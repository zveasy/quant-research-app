from __future__ import annotations

import json
import os
from typing import Dict

import boto3
from prometheus_client import Counter, start_http_server
from scipy.stats import ks_2samp

SQS_QUEUE = os.getenv("DRIFT_SQS", "drift-alerts")
CW_LOG_GROUP = os.getenv("DRIFT_LOG_GROUP", "drift-monitor")
EXPORTER_PORT = int(os.getenv("DRIFT_EXPORTER_PORT", "9300"))

sqs = boto3.client("sqs")
logs = boto3.client("logs")

rollbacks = Counter("model_rollbacks", "Triggered rollbacks")


def check_drift(today: Dict[str, float], baseline: Dict[str, float]) -> None:
    p = ks_2samp(list(today.values()), list(baseline.values())).pvalue
    logs.put_log_events(logGroupName=CW_LOG_GROUP, logStreamName="drift", logEvents=[{"timestamp": int(os.times().elapsed * 1000), "message": json.dumps({"p": p})}])
    if p < 0.01:
        sqs.send_message(QueueUrl=SQS_QUEUE, MessageBody="ROLLBACK")
        rollbacks.inc()


def main() -> None:
    start_http_server(EXPORTER_PORT)
    # Example usage with dummy data
    today = {"mean": 0.5, "std": 1.2}
    baseline = {"mean": 0.4, "std": 1.1}
    check_drift(today, baseline)


if __name__ == "__main__":
    main()
