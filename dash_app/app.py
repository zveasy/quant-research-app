# In: dash_app/app.py

import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
import numpy as np
import dash_bootstrap_components as dbc
import duckdb
import os
import json 

# --- Data Loading Functions ---

def load_pca_data():
    """Loads multi-stock data for the PCA dashboard."""
    try:
        script_dir = os.path.dirname(__file__)
        csv_path = os.path.join(script_dir, '..', 'sample_data', 'multi_stock.csv')
        df = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
        returns = np.log(df / df.shift(1)).dropna()
        return returns
    except FileNotFoundError:
        print("Error: sample_data/multi_stock.csv not found.")
        return pd.DataFrame()

def load_candidates_from_db():
    """
    Loads all candidates from the DuckDB database and immediately formats
    the 'rationale' column into a display-friendly string.
    """
    try:
        script_dir = os.path.dirname(__file__)
        db_path = os.path.join(script_dir, '..', 'asset_universe.duckdb')
        con = duckdb.connect(database=db_path, read_only=True)
        df = con.execute("""
            SELECT symbol, fit_score, predictability_score_rmse AS predictability_score, rationale, recorded_at
            FROM candidates ORDER BY fit_score DESC
        """).fetchdf()
        con.close()

        if df.empty:
            return pd.DataFrame()

        # --- CORRECTED RATIONALE FORMATTING ---
        def format_rationale(r):
            # This function now correctly handles a Python list from DuckDB
            if isinstance(r, list):
                return "\n".join([f"• {item}" for item in r])
            
            # Fallback for data that might be a JSON string
            try:
                items = json.loads(r) 
                if isinstance(items, list):
                    return "\n".join([f"• {item}" for item in items])
            except (TypeError, json.JSONDecodeError):
                return str(r) # Return as a string if all else fails
            return str(r)
        
        df['rationale'] = df['rationale'].apply(format_rationale)
        # ----------------------------------------

        return df
    except Exception as e:
        print(f"Error loading from DuckDB: {e}")
        return pd.DataFrame()

# --- App Initialization & Layout ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("Quant Research Dashboard", className="my-4 text-center"),
    dbc.Tabs(id="tabs-main", children=[
        
        dbc.Tab(label="PCA Factor Analysis", children=[
            dbc.Container([
                html.H3("Principal Component Analysis", className="mt-3"),
                html.P("Analyze latent factors in asset returns."),
                dcc.Dropdown(
                    id='n-components',
                    options=[{'label': str(i), 'value': i} for i in range(1, 4)],
                    value=2, clearable=False, className="mb-3"
                ),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='explained-variance'), width=6),
                    dbc.Col(dcc.Graph(id='pca-scatter'), width=6)
                ])
            ], fluid=True)
        ]),

        dbc.Tab(label="Universe Scout", children=[
            dbc.Container([
                html.H3("AI Asset Screener", className="mt-3"),
                html.P("Filter and review assets scored by the AI agent."),
                dbc.Row([
                    dbc.Col(dcc.Slider(id='fit-score-slider', min=0, max=100, step=5, value=70, marks={i: str(i) for i in range(0, 101, 10)}))
                ], className="my-4"),
                dbc.Row(dbc.Col([
                    html.H4("Matching Candidates"),
                    dash_table.DataTable(
                        id='candidates-table',
                        columns=[
                            {'name': 'Symbol', 'id': 'symbol'},
                            {'name': 'AI Fit Score', 'id': 'fit_score'},
                            {'name': 'Predictability', 'id': 'predictability_score'},
                            {'name': 'Recorded At', 'id': 'recorded_at'},
                            {'name': 'AI Rationale', 'id': 'rationale'},
                        ],
                        page_size=15,
                        sort_action='native',
                        filter_action='native',
                        style_cell={'textAlign': 'left'},
                        style_header={'fontWeight': 'bold'},
                        style_table={'overflowX': 'auto'},
                        style_cell_conditional=[
                            {'if': {'column_id': 'rationale'}, 'whiteSpace': 'pre-line'}
                        ]
                    )
                ]))
            ], fluid=True)
        ]),
    ])
], fluid=True)

# --- Callbacks ---

@app.callback(
    Output('explained-variance', 'figure'),
    Output('pca-scatter', 'figure'),
    Input('n-components', 'value')
)
def update_pca_charts(n):
    returns = load_pca_data()
    if returns.empty:
        return px.bar(title="No Data"), px.scatter(title="No Data")
    pca = PCA(n_components=n)
    X = pca.fit_transform(returns)
    fig1 = px.bar(x=[f"PC{i+1}" for i in range(n)], y=pca.explained_variance_ratio_, title="Explained Variance")
    fig2 = px.scatter(x=X[:, 0], y=X[:, 1] if n > 1 else [0]*len(X), title="PCA Projection", hover_name=returns.index)
    return fig1, fig2

@app.callback(
    Output('candidates-table', 'data'),
    Input('fit-score-slider', 'value')
)
def update_candidates_table(min_fit_score):
    # The data is now pre-formatted, so this callback is much simpler.
    df = load_candidates_from_db()
    if df.empty:
        return []

    filtered_df = df[df['fit_score'] >= min_fit_score]
    return filtered_df.to_dict('records')

# --- Main Run Block ---
if __name__ == '__main__':
    app.run(debug=True)
