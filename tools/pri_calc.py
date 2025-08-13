#!/usr/bin/env python3
"""PRI (Project Readiness Index) calculator.

This lightweight script is executed in CI. It calculates a simple
percentage score based on the presence of key evidence/artifact folders
in the repository and posts the result as a comment on the pull request
that triggered the workflow.

Environment variables expected (injected by GitHub Actions):
GITHUB_TOKEN      – token with `repo` scope to allow commenting.
GITHUB_REPOSITORY – e.g. "owner/repo".
GITHUB_EVENT_PATH – path to the event payload JSON.

The rubric here is intentionally kept simple: each required folder found
adds an equal weight. Adjust `REQUIRED_PATHS` or extend the logic to
weigh paths differently if desired.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import List

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REQUIRED_PATHS: List[str] = [
    "docs/research",
    "docs/data",
    "engine/tests",
    "engine/fixtures/clock",
    "oms/tca",
    "oms/recon/fixtures",
    "risk",
    "ops/runbooks",
    "security",
]

COMMENT_HEADER = "PRI: "  # The comment will be like "PRI: 88%"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def calculate_pri() -> int:
    """Return PRI as an integer percentage based on REQUIRED_PATHS."""
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    present = 0
    for rel_path in REQUIRED_PATHS:
        if (repo_root / rel_path).exists():
            present += 1
    return round(100 * present / len(REQUIRED_PATHS))


def read_pr_number(event_path: str) -> int:
    """Extract pull request number from the GitHub event payload."""
    with open(event_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    # Both pull_request and issue events have "number" at root
    return data.get("number") or data.get("pull_request", {}).get("number")


def post_comment(token: str, repo: str, pr_number: int, message: str) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"body": message}
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    if resp.status_code >= 300:
        print("Failed to post comment", resp.status_code, resp.text, file=sys.stderr)
        resp.raise_for_status()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not (token and repo and event_path):
        print("Missing required GitHub environment variables.", file=sys.stderr)
        sys.exit(1)

    pri_score = calculate_pri()
    pr_number = read_pr_number(event_path)

    if not pr_number:
        print("Could not determine PR number from event.", file=sys.stderr)
        sys.exit(1)

    comment_body = f"{COMMENT_HEADER}{pri_score}%"
    post_comment(token, repo, pr_number, comment_body)
    print(comment_body)


if __name__ == "__main__":
    main()
