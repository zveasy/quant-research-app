# Data Lineage Diagram

```mermaid
flowchart TD
    subgraph Ingestion
        raw_kafka["Raw Market Data (Kafka)"]
        corp_act["Corporate Actions API"]
        ref_data["Ref Data FTP"]
    end

    raw_kafka --> bronze[(Bronze / Raw Parquet)]
    corp_act --> bronze
    ref_data --> bronze

    bronze --> silver[(Silver / Cleaned)]
    silver --> gold[(Gold / Point-in-Time Views)]
    gold --> feature_store["Feature Store"]
    silver --> backtests[(Backtest Sample Sets)]
    gold --> dashboards["BI Dashboards"]
```

**Key Concepts**

* **Bronze**: as-is landing zone, schema-on-read.
* **Silver**: validated, de-duplicated, conforming types; bad-tick filter applied here.
* **Gold**: point-in-time adjusted views (corporate-actions, survivorship-safe).

All downstream consumers (research, OMS, risk) *must* source from **Gold** to guarantee historical integrity.
