"""Daily cloud cost alert via CloudZero API."""

from __future__ import annotations

import os
import requests

DAILY_LIMIT = float(os.environ.get("DAILY_LIMIT", "1000"))
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")
CLOUDZERO_TOKEN = os.environ.get("CLOUDZERO_TOKEN")


def fetch_spend() -> float:
    headers = {"Authorization": f"Bearer {CLOUDZERO_TOKEN}"}
    resp = requests.get("https://api.cloudzero.com/spend", headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return float(data.get("aws", 0)) + float(data.get("azure", 0))


def send_alert(amount: float) -> None:
    if not SLACK_WEBHOOK:
        return
    text = f"Daily cloud spend ${amount:.2f} exceeds limit ${DAILY_LIMIT:.2f}"
    requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)


def main() -> None:
    spend = fetch_spend()
    if spend > DAILY_LIMIT:
        send_alert(spend)


if __name__ == "__main__":
    main()
