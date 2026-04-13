#!/bin/bash
set -euo pipefail

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/opt/quant-research/backups/$STAMP"
mkdir -p "$BACKUP_DIR"

cd /opt/quant-research/quant-research-platform
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/postgres.sql"
tar -czf "$BACKUP_DIR/data.tgz" data

echo "Backup saved to $BACKUP_DIR"
