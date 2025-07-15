import asyncio
import os

import httpx
from prometheus_client import Gauge, start_http_server
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_HEALTH = os.getenv("API_HEALTH_URL", "http://localhost:8000/health")
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", "8001"))

avg_latency_gauge = Gauge("avg_latency_ms", "Average request latency")
error_rate_gauge = Gauge("error_rate", "Error rate")
qps_gauge = Gauge("qps", "Queries per second")


async def collect_metrics(redis: Redis, client: httpx.AsyncClient) -> None:
    while True:
        try:
            latency = await redis.get("metrics:avg_latency")
            qps = await redis.get("metrics:qps")
            avg_latency_gauge.set(float(latency or 0.0))
            qps_gauge.set(float(qps or 0.0))
        except Exception:
            pass
        try:
            resp = await client.get(API_HEALTH, timeout=2)
            error_rate_gauge.set(0.0 if resp.status_code == 200 else 1.0)
        except Exception:
            error_rate_gauge.set(1.0)
        await asyncio.sleep(5)


async def main() -> None:
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    async with httpx.AsyncClient() as client:
        start_http_server(EXPORTER_PORT)
        await collect_metrics(redis, client)


if __name__ == "__main__":
    asyncio.run(main())
