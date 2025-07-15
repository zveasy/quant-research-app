"""Track privacy budget with a simple Moments Accountant."""
from __future__ import annotations

import json
import os
import boto3
import requests


class PrivacyTracker:
    def __init__(self, s3_uri: str, slack_webhook: str):
        self.s3_uri = s3_uri
        self.slack_webhook = slack_webhook
        self.epsilon = 0.0
        self.log: list[dict] = []

    def record(self, delta: float) -> None:
        self.epsilon += delta
        self.log.append({"round": len(self.log) + 1, "epsilon": self.epsilon})

    def persist(self) -> None:
        bucket, key = self.s3_uri[5:].split("/", 1)
        boto3.client("s3").put_object(
            Bucket=bucket, Key=key, Body=json.dumps(self.log).encode()
        )

    def send_digest(self) -> None:
        text = f"Current epsilon: {self.epsilon:.2f}"
        requests.post(self.slack_webhook, json={"text": text})


def main() -> None:
    tracker = PrivacyTracker(os.environ["PRIV_S3"], os.environ["SLACK_WEBHOOK"])
    tracker.record(float(os.environ.get("DELTA_EPS", "0.1")))
    tracker.persist()
    tracker.send_digest()


if __name__ == "__main__":
    main()
