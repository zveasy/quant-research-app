# 📊 AI-Powered Universe Scout & Quant Research Dashboard

This project is an end-to-end pipeline for discovering, enriching, and ranking financial assets using quantitative factors and an AI agent. It features a multi-tab Dash web application for visualizing both factor analysis and the AI-driven asset screening results.

---

## ✨ Features

- **Automated Pipeline**: A command-line script (`create_db.py`) that runs the entire data workflow.
- **Factor Library**: A modular system for calculating quantitative factors like Value (Price-to-Book), Momentum, and Dividend Yield.
- **AI Asset Scoring**: Uses an AI agent (in developer mode) to provide a "Fit Score" and rationale for each asset's suitability.
- **Supply Chain Explorer**: Suggests supplier stocks for major tech companies like Nvidia or Apple.
- **Data Lake Storage**: Saves enriched asset data to fast Parquet files and logs metadata in a DuckDB database for quick queries.
- **SEC Filing Summaries**: Fetches the latest filings and uses GPT-4o to summarize risks.
- **Interactive Dashboard**: A multi-tab Dash application for:
    1.  **PCA Factor Analysis**: Visualize latent factors across a basket of stocks.
    2.  **Equities Scout**: Review the AI-scored equity candidates.
    3.  **Currencies**: Screen currency pairs with FX carry metrics.
    4.  **Carbon Credits**: Explore carbon credit opportunities.
    5.  **Green Bonds**: Browse green bond issuances with duration info.
- **CI/CD Ready**: Includes a GitHub Actions workflow to automatically run tests on every push, ensuring code quality and stability.
- **Legislation Insights**: Fetches recent bills and uses GPT-4o to summarize potential market impact.
- **Fed Rate Tracking**: Pulls the latest Federal Funds Rate from FRED and records monthly changes to gauge borrowing conditions.
- **Option Pricing Model**: Provides a Black-Scholes implementation for pricing European call and put options.

---

## 📁 Project Structure


jv-quant-research/
├── .github/workflows/         # CI/CD workflows
│   └── ci.yml
├── dash_app/                  # Contains the Dash web application
│   └── app.py
├── factors/                   # Modules for calculating quant factors
│   ├── value.py
│   └── momentum.py
├── universe_scouter/          # Core pipeline modules
│   ├── ai_agent.py
│   ├── enrichers.py
│   └── storage.py
├── political/                 # Tools for legislation analysis
│   └── legislation.py
├── tests/                     # PyTest suite
│   └── test_pipeline.py
├── create_db.py               # Main script to run the data pipeline
├── asset_universe.duckdb      # Local database for the dashboard
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables
└── README.md                  # This file


---

## 🚀 Getting Started

### Docker Dev Container

If you're using an editor like VS Code with the Dev Containers or GitHub Codespaces extension,
simply open this project and the included configuration will automatically build and start the
Docker environment. This ensures a consistent setup across different operating systems.

### 1. Setup Environment

First, create and activate a Python virtual environment.

```bash
# Create the environment
python3.11 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate
```

2. Install Dependencies
Install all required packages from the requirements.txt file.

```bash
pip install -r requirements.txt
```

3. Set Up Environment Variables
Create a `.env` file in the project root by copying the example file.

cp .env.example .env

Edit the `.env` file and add your OpenAI API key.  You can also change
`DB_PATH` if you want the DuckDB file stored somewhere else.

⚙️ How to Use
There are two main parts to this project: running the data pipeline and viewing the dashboard.

1. Run the Data Pipeline
Run `create_db.py` to discover, enrich, and score the assets. The
database will be written to the location specified by `DB_PATH` (or
`./asset_universe.duckdb` by default) for the dashboard to read.

python create_db.py

2. Launch the Dashboard
To view the results in the interactive web application, run the app.py script.

python dash_app/app.py

The dashboard will be available at http://127.0.0.1:8050.

3. Run the Tests
To verify that all components are working as expected, run the pytest suite.

# This command will automatically discover and run all tests
PYTHONPATH=$(pwd) pytest

## 📸 Example Screenshots

Below are sample images of the new dashboard tabs.

| Currencies | Carbon Credits | Green Bonds |
|-----------|---------------|-------------|
| ![Currencies](docs/screenshots/currencies.ppm) | ![Carbon Credits](docs/screenshots/carbon_credits.ppm) | ![Green Bonds](docs/screenshots/green_bonds.ppm) |


## 🧩 New: VM-Ready OpenAI + QuantEngine Platform Scaffold

A deployable mono-repo scaffold is now included at `quant-research-platform/` with:
- FastAPI `agent-api` using OpenAI Responses API tool schemas
- `worker` job runner skeleton
- `quantengine-bridge` safety/export boundary
- Docker Compose stack + GCP startup/create scripts

See `quant-research-platform/README.md` for usage.
