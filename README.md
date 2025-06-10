📄 README.md
markdown
Copy
Edit
# 📊 PCA Dashboard — Quant Research Tool

This project builds a multi-ticker PCA dashboard for exploratory market analysis using Python, Dash, and Docker. The dashboard visualizes asset return correlations and principal components across a rolling time window.

---

## 📁 Project Structure

jv-quant-research/
├── dash_app/
│ └── app.py # Dash web app (PCA dashboard)
├── dataprep/
│ └── init.py # get_returns, get_volatility, to_freq
├── sample_data/
│ └── multi_stock.csv # Sample price data for AAPL, MSFT, AMZN
├── notebooks/
│ └── explore_market.ipynb # Jupyter EDA (heatmaps, volatility)
├── Dockerfile # Docker config to containerize the app
├── docker-compose.yml # Local service runner w/ healthcheck
├── requirements.txt # Python dependencies
└── README.md

yaml
Copy
Edit

---

## 🚀 Features

- 📈 Rolling volatility and heatmap visualizations via Jupyter
- 🧮 PCA dashboard built with Dash + Plotly
- 📦 Fully containerized via Docker
- ✅ Healthcheck-enabled Docker Compose setup
- ☁️ Ready for deployment to AWS (via ECR + ECS or Fargate)

---

## 🐍 Local Development

### ✅ 1. Set up Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
▶️ 2. Run Dash app locally
bash
Copy
Edit
python dash_app/app.py
App will be available at: http://localhost:8050

🐳 Run with Docker
🔁 1. Build container
bash
Copy
Edit
docker build -t pca-dashboard .
▶️ 2. Run container
bash
Copy
Edit
docker run -p 8050:8050 pca-dashboard
App will be running at http://localhost:8050

⚙️ Docker Compose (with healthcheck)
bash
Copy
Edit
docker compose up --build
📦 Ready for AWS
This repo is ready to be:

Pushed to a GitHub repo

Built and stored in AWS ECR

Deployed via ECS/Fargate or integrated into a larger VPC service mesh

🧪 Future Extensions
Connect to REST API for live ticker selection

Add login + access control (Flask-Login)

Deploy behind reverse proxy (NGINX)

Attach database (e.g., PostgreSQL + TimescaleDB)

Add CI/CD (GitHub Actions → Docker → ECR)

👤 Author
Joshua Veasy
Quantitative research tools built with Python, data, and curiosity.

yaml
Copy
Edit

---

Let me know if you want a version tailored for:
- A GitHub portfolio
- A job submission
- Or internal AWS team handoff (with ECR tags, CI/CD notes, etc.)






