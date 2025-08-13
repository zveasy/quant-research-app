# Time Synchronization Runbook

Maintaining sub-millisecond clock accuracy is critical for order-timestamping, latency attribution, and regulatory reporting (MiFID II RTS 25).

## Budget

| Component | Max Skew |
|-----------|----------|
| Trading hosts | ±250 µs |
| Databases / Kafka brokers | ±500 µs |
| Monitoring & BI nodes | ±1 ms |

CI fails if `ntp_offset` > 200 µs on any trading host.

## Procedure (chrony)

1. Ensure `chronyd` is installed and enabled:
   ```bash
   sudo apt-get install chrony -y
   sudo systemctl enable --now chronyd
   ```
2. Configure `/etc/chrony/chrony.conf`:
   ```
   server time.google.com iburst maxdelay 0.05
   server time.cloudflare.com iburst maxdelay 0.05
   makestep 0.2 3
   driftfile /var/lib/chrony/drift
   rtcsync
   ```
3. Restart service:
   ```bash
   sudo systemctl restart chronyd
   ```
4. Verify status:
   ```bash
   chronyc tracking
   chronyc sources -v
   ```
   Offset should be within ±100 µs and RMS jitter <50 µs.

## Monitoring

Prometheus exporter `chrony_exporter` exposes `chrony_current_correction_seconds`.
Alert rule:
```yaml
- alert: ClockSkewHigh
  expr: abs(chrony_current_correction_seconds) > 0.0002
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Clock skew exceeds 200µs"
```

Grafana dashboard: *Infra / Time Sync* displays offset, frequency, and source quality.
