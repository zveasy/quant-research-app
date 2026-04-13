# Deployment

1. Create Ubuntu 24.04 VM (4 vCPU / 16 GB RAM / 100-200 GB SSD)
2. Attach startup script: `infra/gcp/startup.sh`
3. SSH in and validate:

```bash
cd /opt/quant-research/quant-research-platform
docker compose ps
docker compose logs -f agent-api
```
