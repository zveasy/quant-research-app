#!/bin/bash
set -euo pipefail

PROJECT_ID="your-project-id"
ZONE="us-east4-b"
INSTANCE_NAME="quant-research-vm"
MACHINE_TYPE="e2-standard-4"

gcloud config set project "$PROJECT_ID"

gcloud compute instances create "$INSTANCE_NAME" \
  --zone="$ZONE" \
  --machine-type="$MACHINE_TYPE" \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server \
  --metadata-from-file startup-script=infra/gcp/startup.sh
