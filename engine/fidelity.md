# Latency & Slippage Model v1

This document describes the first-pass execution-cost model calibrated to Interactive Brokers (retail path) log data.

## Model

Market-impact cost (bps from mid) is decomposed into:

```
IS = k0 + k1 * spread_bps + k2 * (latency_ms / 1000) + ε
```

Parameter values (calibrated on fixture day 2024-06-14):

| Param | Value | Notes |
|-------|-------|-------|
| k0    | 1.2   | baseline venue+fees effect |
| k1    | 0.5   | half-spread capture assumption |
| k2    | 0.9   | adverse drift per second |

Noise term ε ~ N(0, σ²) with σ = 3 bps.

## Calibration Procedure

1. Parse ZeroMQ execution logs to extract:
   • `latency_ms` (order‐to‐fill RTT)  
   • `spread_bps` at order entry  
   • realised implementation shortfall `is_bps`.
2. Fit OLS with intercept.
3. Store parameters in `engine/models/cost_model.py` so that CI can compute IS estimates.
4. CI test asserts mean absolute percentage error (MAPE) < 20 % versus fixture logs.

## Fixture Logs

`engine/fixtures/latency/sample_logs.csv` — anonymised single-day set with 500 fills.
