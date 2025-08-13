# Research Methodology

## IS/OOS Split & Walk-Forward Protocol

| Window | Train (IS) span | Test (OOS) span |
|--------|-----------------|-----------------|
| 1      | 2000-01-01 → 2004-12-31 | 2005-01-01 → 2005-12-31 |
| 2      | 2001-01-01 → 2005-12-31 | 2006-01-01 → 2006-12-31 |
| ⋯      | ⋯ | ⋯ |

Rules:
1. **Monotonic index** – data must be sorted ascending by timestamp.
2. **Non-overlapping OOS windows** – default `step = test_size`.
3. **Minimum look-forward** – OOS ≥ 6 months or 125 trading days.
4. **No label leakage** – target generation must occur strictly *after* all feature engineering.

## Leak-Test Policy

We run automated checks:
* **Target peeking** – ensure features are not computed with knowledge of the target value at *t*.
* **Post-event joins** – prevent joining corporate-action info with future effective dates.
* **Future leaks** – any join on `df.shift(-k)` with `k>0` is forbidden in production code.

All checks live in `research/leak_checks.py` and gate CI.

## Sharpe CI Method

For every backtest produced by the CI, we compute:
```
annualised_sharpe = sqrt(252) * mean(returns) / std(returns)
```
A PR **fails** if the OOS annualised Sharpe of the walk-forward schedule is < **0.75** or degrades by > **25 bps** relative to `main`.

## Capacity Methodology

Capacity estimates follow Almgren-Chriss impact:
```
slippage(Q) = α·Q + β·Q²
```
We compute **net PnL vs. fill size Q** across OOS windows, fit a polynomial, and estimate the **capacity-limit** as the Q where marginal slippage = alpha.
Outputs:
* `docs/research/figs/capacity_curve.png`
* `capacity_results.csv` with `(Q, net_PnL, IS_bps)`

