from __future__ import annotations

import os
import time
from typing import Dict, List

import requests
import torch
import torch.nn as nn
import numpy as np

ALERTMANAGER_URL = os.getenv("ALERTMANAGER_URL", "http://alertmanager:9093/api/v1/alerts")
REMOTE_WRITE_ENDPOINT = os.getenv("REMOTE_WRITE_ENDPOINT", "http://prometheus:9090/api/v1/write")
METRICS_URL = os.getenv("NODE_EXPORTER_URL", "http://localhost:9100/metrics")
WINDOW = int(os.getenv("LSTM_WINDOW", "30"))


class LSTMModel(nn.Module):
    def __init__(self, features: int, hidden: int = 32):
        super().__init__()
        self.lstm = nn.LSTM(features, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return torch.sigmoid(self.fc(out))


def parse_metrics(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for line in text.splitlines():
        if line.startswith("node_load1"):
            out["load1"] = float(line.split()[-1])
        if line.startswith("node_memory_MemAvailable_bytes"):
            out["mem_avail"] = float(line.split()[-1])
    return out


def fetch_metrics() -> Dict[str, float]:
    r = requests.get(METRICS_URL, timeout=5)
    r.raise_for_status()
    return parse_metrics(r.text)


def remote_write(metrics: Dict[str, float]) -> None:
    # Simplified remote write as JSON for demo purposes
    requests.post(REMOTE_WRITE_ENDPOINT, json=metrics, timeout=5)


def send_alert(prob: float) -> None:
    alert = [
        {
            "labels": {"alertname": "NodeFailurePredicted"},
            "annotations": {"summary": f"failure_prob={prob:.2f}"},
        }
    ]
    requests.post(ALERTMANAGER_URL, json=alert, timeout=5)


def train_model(data: List[Dict[str, float]]) -> LSTMModel:
    arr = np.array([[d["load1"], d["mem_avail"]] for d in data], dtype=np.float32)
    X = []
    y = []
    for i in range(len(arr) - WINDOW - 1):
        X.append(arr[i : i + WINDOW])
        y.append(arr[i + WINDOW, 0])
    X_t = torch.tensor(np.stack(X))
    y_t = torch.tensor(y).unsqueeze(1)
    model = LSTMModel(features=2)
    loss_fn = nn.MSELoss()
    opt = torch.optim.Adam(model.parameters())
    for _ in range(50):
        opt.zero_grad()
        out = model(X_t)
        loss = loss_fn(out, y_t)
        loss.backward()
        opt.step()
    return model


def main() -> None:
    history: List[Dict[str, float]] = []
    model: LSTMModel | None = None
    while True:
        metrics = fetch_metrics()
        remote_write(metrics)
        history.append(metrics)
        if len(history) > WINDOW * 2:
            model = train_model(history[-WINDOW * 2 :])
            seq = torch.tensor([[metrics["load1"], metrics["mem_avail"]]], dtype=torch.float32).unsqueeze(0)
            prob = float(model(seq))
            if prob > 0.8:
                send_alert(prob)
        time.sleep(60)


if __name__ == "__main__":
    main()
