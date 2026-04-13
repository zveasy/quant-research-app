#!/bin/bash
set -euo pipefail

PROJECT_ID="your-project-id"
gcloud config set project "$PROJECT_ID"

gcloud compute firewall-rules create quant-research-allow-web \
  --allow tcp:80,tcp:443,tcp:22 \
  --target-tags http-server,https-server \
  --description="Allow SSH/HTTP/HTTPS for quant research VM" || true
