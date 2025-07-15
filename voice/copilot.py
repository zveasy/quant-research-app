"""Voice Copilot WebSocket service."""
from __future__ import annotations

import asyncio
import json
import requests
from fastapi import FastAPI, WebSocket
import whisper

app = FastAPI()
model = whisper.load_model("tiny")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    audio = bytearray()
    async for msg in ws.iter_bytes():
        if msg == b"__end__":
            break
        audio.extend(msg)
    result = model.transcribe(bytes(audio))
    text = result.get("text", "")
    if "explain drawdown" in text.lower():
        resp = requests.get("http://localhost:8000/perf").json()
    elif "place order" in text.lower():
        resp = requests.post("http://localhost:8000/orders").json()
    else:
        resp = {"message": "unrecognized"}
    await ws.send_text(json.dumps(resp))
    with open("voice_session.log", "a") as f:
        f.write(text + "\n")
    await ws.close()
