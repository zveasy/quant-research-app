"""Run chaos experiments defined in chaos/experiments.yaml."""
from __future__ import annotations

import os
import yaml
import requests

GREMLIN_URL = os.environ.get("GREMLIN_URL", "https://api.gremlin.com")
PROM_URL = os.environ.get("PROM_URL", "http://localhost:9090")
JIRA_URL = os.environ.get("JIRA_URL", "https://your-jira-instance/rest/api/2/issue")


def apply_fault(fault: dict) -> None:
    requests.post(f"{GREMLIN_URL}/attack", json=fault)


def query_slo() -> float:
    r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": "job:quant_api:availability"})
    result = r.json()["data"]["result"][0]["value"][1]
    return 1 - float(result)


def create_ticket(burn: float) -> None:
    requests.post(JIRA_URL, json={"fields": {"summary": f"SLO burn {burn:.2%}", "description": PROM_URL}})


def main() -> None:
    with open("chaos/experiments.yaml") as f:
        config = yaml.safe_load(f)
    for exp in config.get("experiments", []):
        apply_fault(exp)
    burn = query_slo()
    create_ticket(burn)


if __name__ == "__main__":
    main()
