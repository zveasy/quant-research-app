# Model Card: AI Asset Screener

## 1. Model Details

* **Model Name:** AI Asset Screener (Universe Scout)
* **Version:** 1.0
* **Model Type:** Hybrid System combining quantitative factors with a Large Language Model (LLM) for suitability scoring.
* **Author:** Joshua Veasy
* **Contact:** [Your Email or GitHub Profile]

---

## 2. Intended Use

* **Primary Use:** This system is designed to automatically screen a universe of assets (starting with US equities) and rank them based on their suitability for inclusion in a quantitative trading portfolio.
* **Primary Users:** Quant Researchers, Portfolio Managers.
* **Out-of-Scope Uses:** This model is not a direct trade signal generator. It does not provide buy/sell recommendations. It is a research and filtering tool designed to generate a high-quality list of assets for further strategy development.

---

## 3. How It Works: The Data Pipeline

The system operates as an end-to-end data pipeline in the following stages:

1.  **Discovery:** Identifies a list of tradable assets (e.g., most active stocks).
2.  **Enrichment:** For each asset, it calculates a suite of quantitative factors:
    * **Predictability:** ARIMA-based RMSE score.
    * **Value:** Price-to-Book (P/B) Ratio.
    * **Quality:** Debt-to-Equity (D/E) and Return on Equity (ROE).
    * **Momentum:** 12-Month Price Return.
    * **Volatility:** 1-Year Annualized Volatility.
    * **Alternative Data:** Google Trends score.
3.  **AI Scoring:** A detailed summary of the enriched data is sent to an AI model (GPT-4o), which provides a `Fit Score` (0-100) and a qualitative `rationale`.
4.  **Storage:** The final, scored results are saved to a Parquet data lake and a DuckDB database for analysis.
5.  **Back-testing:** A back-testing module (`vectorbt`) is used to simulate the performance of strategies based on the top-ranked assets.

---

## 4. Training Data & Evaluation

* **Quantitative Factors:** Based on standard financial formulas using historical price and fundamental data from `yfinance`.
* **AI Model:** Utilizes the pre-trained `gpt-4o` model. A "developer mode" is included for testing, which uses a hardcoded heuristic response.
* **Evaluation:** The system's output is evaluated via back-testing. The primary metrics are Total Return, Sharpe Ratio, and Max Drawdown of a portfolio constructed from the top N AI-scored assets.

---

## 5. Limitations & Bias

* **Data Source Dependency:** The model relies entirely on data provided by the `yfinance` API. Outages or data errors from the source will directly impact results.
* **Lookahead Bias:** The back-tester uses historical data and is carefully constructed to avoid lookahead bias, but this should always be monitored.
* **LLM Hallucination:** When not in developer mode, the LLM could potentially provide a rationale that is not fully supported by the input data. The "Prompt-Engineering Pass" (Sprint 05) was designed to mitigate this by grounding the prompt in data.
* **Factor limitations:** The current factor library is foundational. It does not yet include more advanced factors (e.g., macroeconomic data, detailed ESG scores).

---

## 6. How to Use & Monitor

* The pipeline is run automatically via the `scheduler.yml` GitHub Actions workflow every day at 05:00 UTC.
* The results can be viewed on the interactive Dash application.
* The system's health is monitored via the CI pipeline (`ci.yml`), which runs all `pytest` tests on every code change.