# 📊 AI-Powered Universe Scout & Quant Research Dashboard

This project is an end-to-end pipeline for discovering, enriching, and ranking financial assets using quantitative factors and an AI agent. It features a multi-tab Dash web application for visualizing both factor analysis and the AI-driven asset screening results.

---

## ✨ Features

- **Automated Pipeline**: A command-line script (`create_db.py`) that runs the entire data workflow.
- **Factor Library**: A modular system for calculating quantitative factors like Value (Price-to-Book) and Momentum.
- **AI Asset Scoring**: Uses an AI agent (in developer mode) to provide a "Fit Score" and rationale for each asset's suitability.
- **Data Lake Storage**: Saves enriched asset data to fast Parquet files and logs metadata in a DuckDB database for quick queries.
- **Interactive Dashboard**: A two-tab Dash application for:
    1.  **PCA Factor Analysis**: Visualize latent factors across a basket of stocks.
    2.  **Universe Scout**: A filterable, sortable table to review the AI-scored asset candidates.
- **CI/CD Ready**: Includes a GitHub Actions workflow to automatically run tests on every push, ensuring code quality and stability.

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
├── tests/                     # PyTest suite
│   └── test_pipeline.py
├── create_db.py               # Main script to run the data pipeline
├── asset_universe.duckdb      # Local database for the dashboard
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables
└── README.md                  # This file


---

## 🚀 Getting Started

### 1. Setup Environment

First, create and activate a Python virtual environment.

```bash
# Create the environment
python3 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

2. Install Dependencies
Install all required packages from the requirements.txt file.

pip install -r requirements.txt

3. Set Up API Keys
Create a .env file in the project root by copying the example file.

cp .env.example .env

Now, edit the .env file and add your OpenAI API key.

⚙️ How to Use
There are two main parts to this project: running the data pipeline and viewing the dashboard.

1. Run the Data Pipeline
To discover, enrich, and score the assets, run the create_db.py script. This will generate the asset_universe.duckdb file that the dashboard reads from.

python create_db.py

2. Launch the Dashboard
To view the results in the interactive web application, run the app.py script.

python dash_app/app.py

The dashboard will be available at http://127.0.0.1:8050.

3. Run the Tests
To verify that all components are working as expected, run the pytest suite.

# This command will automatically discover and run all tests
pytest
