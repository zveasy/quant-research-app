# Quant Research App Documentation

## Overview
This app is a modular quant research platform for asset discovery, enrichment, ranking, and analytics. It supports real-time broadcasting, feature engineering, option pricing, stress testing, and interactive dashboards.

---

## Architecture Diagram

![Quant Research App Architecture](screenshots/architecture.png)

---

## Main Components

### 1. Data Pipeline & Database
- **create_db.py**: Builds and populates `asset_universe.duckdb` with asset data.
- **feature_store.py**: Generates and stores engineered features for assets.
- **data_prep/yfinance_utils.py**: Fetches and preprocesses market data.

### 2. Asset Enrichment & Factors
- **factors/**: Contains factor models (PPP, momentum, dividend yield, etc.).
- **risk/stress.py**: Stress testing and scenario analysis.
- **alt_data/**: Alternative data sources (trends, filings).

### 3. Option Pricing
- **option_pricing/black_scholes.py**: Black-Scholes pricing for options.
- **tests/test_option_pricing.py**: Validates pricing logic.

### 4. Real-Time Broadcasting
- **api/publisher.py**: ZMQ publisher broadcasts asset data at sub-millisecond intervals for integration with QuantEngine/C++.
- **tests/test_publisher_zmq.py**: Tests message throughput and dynamic updates.

### 5. Dash & Streamlit Dashboards
- **dash_app/app.py**: Interactive dashboard for asset analytics.
- **streamlit_portal/portal.py**: Streamlit portal for feature exploration.

### 6. Realtime Service
- **realtime_service/service.py**: Real-time data service (Dockerized for deployment).

### 7. Testing & Validation
- **tests/**: Comprehensive test suite for all modules (factor models, publisher, option pricing, etc.).

---

## Data Flow
1. **Pipeline**: `create_db.py` ingests and processes raw data, populates the DuckDB database.
2. **Feature Store**: `feature_store.py` computes features and stores them in the database.
3. **Enrichment**: Factor modules (e.g., PPP, momentum) enrich asset data.
4. **Broadcast**: `api/publisher.py` reads from the database and broadcasts updates via ZMQ.
5. **Dashboards**: Dash and Streamlit apps visualize analytics and features.
6. **Realtime Service**: Optionally provides live data via Dockerized microservice.

---

## Visual Diagrams
- Place architecture and data flow diagrams in `docs/screenshots/` as `.png` or `.ppm` files for easy viewing.
- Example: `docs/screenshots/architecture.png` (create with draw.io, Excalidraw, or similar tools).

---

## Setup & Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run pipeline: `PYTHONPATH=$(pwd) python create_db.py`
3. Start publisher: `PYTHONPATH=$(pwd) python api/publisher.py`
4. Run dashboards: `python dash_app/app.py` or `streamlit run streamlit_portal/portal.py`
5. Run tests: `PYTHONPATH=$(pwd) pytest`

---

## Extending & Integrating
- Add new factor models in `factors/` and corresponding tests in `tests/`.
- Integrate new data sources in `alt_data/`.
- Extend dashboards for new analytics.
- Use ZMQ publisher for integration with external engines (e.g., QuantEngine/C++).

---

## Contact & Contribution
- See `README.md` for contribution guidelines and contact info.

---

## Note
For visual diagrams, add your `.png` or `.ppm` files to `docs/screenshots/` and reference them in this document for easy access.
