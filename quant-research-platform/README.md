# Quant Research Platform (OpenClaw + OpenAI + QuantEngine Bridge)

This scaffold adds a production-minded mono-repo you can run on a single Ubuntu VM and scale out later.

## What you get

- `agent-api`: FastAPI orchestration layer for OpenAI Responses API and internal tools.
- `worker`: background worker skeleton for ingestion/backtests/evals.
- `quantengine-bridge`: strict safety/export boundary for approved strategies.
- `dashboard`: lightweight placeholder service.
- Infra scripts for GCP VM bootstrap and containerized deployment.

## Quick start

```bash
cd quant-research-platform
cp .env.example .env
make up
```

## First API endpoints

- `POST /jobs/research`
- `POST /jobs/backtest`
- `POST /jobs/evaluate`
- `POST /jobs/export`
- `GET /jobs/{id}`
- `GET /strategies`
- `POST /strategies/{id}/approve`

## Notes

- The bridge enforces schema and risk checks and **never places orders**.
- OpenAI integration uses the Responses API with tool schema registration.
- Use `infra/gcp/startup.sh` as the repeatable VM bootstrap script.
