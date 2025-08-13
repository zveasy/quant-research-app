# Data

This directory will store datasets, raw and processed, along with data dictionaries and related documentation.

# Data Engineering Policies

## Corporate Actions Handling

| Event | Adjustment Logic | Notes |
|-------|------------------|-------|
| Stock Split | Multiply historical **price** and **dividend** by split factor; divide **shares outstanding** | Ensures continuity of returns and market cap. |
| Cash Dividend | Subtract dividend from **open** on ex-date for total-return series | Keeps total-return PnL neutral to cash payout timing. |
| Symbol Change | Use FIGI as immutable key, update `ticker` mapping table | Prevents survivorship bias in delisted/renamed equities. |

Rules:
1. Adjustments are applied **once** in the raw market-data warehouse; downstream views inherit adjusted prices.
2. We store both *raw* and *adjusted* values; queries default to adjusted.
3. **Survivorship**: nightly ETL replays symbol history; point-in-time joins use `start_date`/`end_date` columns.

## FIGI Mapping Workflow

```
┌────────┐   OpenFIGI API    ┌────────┐
│ raw.csv ├──────────────────► staging│
└────────┘                    └────────┘
     │ dedupe/validate             │
     ▼                            ▼
┌────────┐   SCD-2 merge     ┌──────────┐
│ dim_figi│◄──────────────────┤ figi_map │
└────────┘                    └──────────┘
```

`data/mapping/figi_map.csv` is a slim export used by local research jobs.

## Survivorship Rules

A security is **active** on date *t* iff `start_date <= t < end_date` (or `end_date` null). Universe queries must filter on these bounds to avoid look-ahead bias.

## Symbol Mapping Example

```python
import pandas as pd
df = pd.read_csv('data/mapping/figi_map.csv')
price = some_price_df  # indexed by FIGI
joined = price.join(df.set_index('figi')['ticker'], how='left')
