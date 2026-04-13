#!/bin/bash
set -euo pipefail

curl -fsS http://localhost:8080/healthz
curl -fsS http://localhost:9001/healthz
curl -fsS http://localhost:3000/healthz

echo "All checks passed"
