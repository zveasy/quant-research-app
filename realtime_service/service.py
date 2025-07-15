from fastapi import FastAPI, WebSocket
from redis.asyncio import Redis
import os
import asyncio

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis = Redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI()


@app.get("/score/{symbol}")
async def get_score(symbol: str):
    value = await redis.get(f"score:{symbol}")
    return {"symbol": symbol, "score": float(value) if value is not None else None}


@app.websocket("/stream")
async def stream(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("__keyspace@0__:score:*")
    try:
        async for message in pubsub.listen():
            if message.get("type") != "pmessage":
                continue
            key = message.get("channel", "").split(":", 1)[1]
            symbol = key.split(":")[-1]
            val = await redis.get(key.replace("__keyspace@0__:", ""))
            await websocket.send_json({"symbol": symbol, "score": float(val) if val else None})
    finally:
        await pubsub.close()
