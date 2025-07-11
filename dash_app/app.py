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
import ast

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

def load_candidates_from_db(asset_class: str | None = None):
    """
    Loads all candidates from the DuckDB database and formats columns
    for clean display in the dashboard.
    """
    try:
        script_dir = os.path.dirname(__file__)
        db_path = os.path.join(script_dir, '..', 'asset_universe.duckdb')
        con = duckdb.connect(database=db_path, read_only=True)
        
        query = "SELECT * FROM candidates"
        params: tuple | None = None
        if asset_class:
            query += " WHERE asset_class = ?"
            params = (asset_class,)
        query += " ORDER BY fit_score DESC"
        if params:
            df = con.execute(query, params).fetchdf()
        else:
            df = con.execute(query).fetchdf()
        con.close()

        if df.empty:
            return pd.DataFrame()

        def format_rationale(r):
            items = []
            if isinstance(r, list):
                items = r
            elif isinstance(r, str) and r.startswith('[') and r.endswith(']'):
                try: 
                    items = ast.literal_eval(r)
                except (ValueError, SyntaxError): 
                    items = [r]
            else:
                items = [str(r)]
            return "\n".join([f"• {item}" for item in items])
        df['rationale'] = df['rationale'].apply(format_rationale)

        # Format other columns
        df['recorded_at'] = pd.to_datetime(df['recorded_at']).dt.strftime('%Y-%m-%d %H:%M')
        if 'momentum_12m' in df.columns:
            df['momentum_12m'] = df['momentum_12m'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        if 'price_to_book' in df.columns:
            df['price_to_book'] = df['price_to_book'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if 'debt_to_equity' in df.columns:
            df['debt_to_equity'] = df['debt_to_equity'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if 'return_on_equity' in df.columns:
            df['return_on_equity'] = df['return_on_equity'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        if 'annualized_volatility' in df.columns:
            df['annualized_volatility'] = df['annualized_volatility'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        if 'google_trends_score' in df.columns:
            df['google_trends_score'] = df['google_trends_score'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        if 'fx_carry' in df.columns:
            df['fx_carry'] = df['fx_carry'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if 'bond_duration' in df.columns:
            df['bond_duration'] = df['bond_duration'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

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
                dbc.Row(dbc.Col(dcc.Slider(id='fit-score-slider', min=0, max=100, step=5, value=70, marks={i: str(i) for i in range(0, 101, 10)}))),
                dbc.Row(dbc.Col([
                    html.H4("Matching Candidates"),
                    dash_table.DataTable(
                        id='candidates-table',
                        columns=[
                            {'name': 'Symbol', 'id': 'symbol'},
                            {'name': 'Asset Class', 'id': 'asset_class'},
                            {'name': 'AI Fit Score', 'id': 'fit_score'},
                            {'name': 'Predictability', 'id': 'predictability_score'},
                            {'name': '12m Momentum', 'id': 'momentum_12m'},
                            {'name': 'Price/Book', 'id': 'price_to_book'},
                            {'name': 'D/E Ratio', 'id': 'debt_to_equity'},
                            {'name': 'ROE', 'id': 'return_on_equity'},
                            {'name': 'Volatility (1Y)', 'id': 'annualized_volatility'},
                            {'name': 'Google Trends', 'id': 'google_trends_score'},
                            {'name': 'FX Carry', 'id': 'fx_carry'},
                            {'name': 'Duration', 'id': 'bond_duration'},
                            {'name': 'Recorded At', 'id': 'recorded_at'},
                            {'name': 'AI Rationale', 'id': 'rationale'},
                        ],
                        page_size=15, sort_action='native', filter_action='native',
                        style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'},
                        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto'},
                        style_cell_conditional=[{'if': {'column_id': 'rationale'}, 'whiteSpace': 'pre-line'}]
                    )
                ]))
            ], fluid=True)
        ]),

        dbc.Tab(label="Currencies", children=[
            dbc.Container([
                html.H3("Currency Screener", className="mt-3"),
                dbc.Row(dbc.Col(dcc.Slider(id='currency-fit-slider', min=0, max=100, step=5, value=70, marks={i: str(i) for i in range(0, 101, 10)}))),
                dbc.Row(dbc.Col([
                    html.H4("Matching Candidates"),
                    dash_table.DataTable(
                        id='currency-table',
                        columns=[
                            {'name': 'Symbol', 'id': 'symbol'},
                            {'name': 'Asset Class', 'id': 'asset_class'},
                            {'name': 'AI Fit Score', 'id': 'fit_score'},
                            {'name': 'Predictability', 'id': 'predictability_score'},
                            {'name': 'FX Carry', 'id': 'fx_carry'},
                            {'name': 'Recorded At', 'id': 'recorded_at'},
                            {'name': 'AI Rationale', 'id': 'rationale'},
                        ],
                        page_size=15, sort_action='native', filter_action='native',
                        style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'},
                        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto'},
                        style_cell_conditional=[{'if': {'column_id': 'rationale'}, 'whiteSpace': 'pre-line'}]
                    )
                ]))
            ], fluid=True)
        ]),

        dbc.Tab(label="Carbon Credits", children=[
            dbc.Container([
                html.H3("Carbon Credit Screener", className="mt-3"),
                dbc.Row(dbc.Col(dcc.Slider(id='carbon-fit-slider', min=0, max=100, step=5, value=70, marks={i: str(i) for i in range(0, 101, 10)}))),
                dbc.Row(dbc.Col([
                    html.H4("Matching Candidates"),
                    dash_table.DataTable(
                        id='carbon-table',
                        columns=[
                            {'name': 'Symbol', 'id': 'symbol'},
                            {'name': 'Asset Class', 'id': 'asset_class'},
                            {'name': 'AI Fit Score', 'id': 'fit_score'},
                            {'name': 'Predictability', 'id': 'predictability_score'},
                            {'name': 'Recorded At', 'id': 'recorded_at'},
                            {'name': 'AI Rationale', 'id': 'rationale'},
                        ],
                        page_size=15, sort_action='native', filter_action='native',
                        style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'},
                        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto'},
                        style_cell_conditional=[{'if': {'column_id': 'rationale'}, 'whiteSpace': 'pre-line'}]
                    )
                ]))
            ], fluid=True)
        ]),

        dbc.Tab(label="Green Bonds", children=[
            dbc.Container([
                html.H3("Green Bond Screener", className="mt-3"),
                dbc.Row(dbc.Col(dcc.Slider(id='green-fit-slider', min=0, max=100, step=5, value=70, marks={i: str(i) for i in range(0, 101, 10)}))),
                dbc.Row(dbc.Col([
                    html.H4("Matching Candidates"),
                    dash_table.DataTable(
                        id='green-table',
                        columns=[
                            {'name': 'Symbol', 'id': 'symbol'},
                            {'name': 'Asset Class', 'id': 'asset_class'},
                            {'name': 'AI Fit Score', 'id': 'fit_score'},
                            {'name': 'Predictability', 'id': 'predictability_score'},
                            {'name': 'Duration', 'id': 'bond_duration'},
                            {'name': 'Recorded At', 'id': 'recorded_at'},
                            {'name': 'AI Rationale', 'id': 'rationale'},
                        ],
                        page_size=15, sort_action='native', filter_action='native',
                        style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'},
                        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto'},
                        style_cell_conditional=[{'if': {'column_id': 'rationale'}, 'whiteSpace': 'pre-line'}]
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
    df = load_candidates_from_db()
    if df.empty:
        return []
    filtered_df = df[df['fit_score'] >= min_fit_score]
    return filtered_df.to_dict('records')

@app.callback(
    Output('currency-table', 'data'),
    Input('currency-fit-slider', 'value')
)
def update_currency_table(min_fit_score):
    df = load_candidates_from_db('currency')
    if df.empty:
        return []
    filtered_df = df[df['fit_score'] >= min_fit_score]
    return filtered_df.to_dict('records')

@app.callback(
    Output('carbon-table', 'data'),
    Input('carbon-fit-slider', 'value')
)
def update_carbon_table(min_fit_score):
    df = load_candidates_from_db('carbon_credit')
    if df.empty:
        return []
    filtered_df = df[df['fit_score'] >= min_fit_score]
    return filtered_df.to_dict('records')

@app.callback(
    Output('green-table', 'data'),
    Input('green-fit-slider', 'value')
)
def update_green_table(min_fit_score):
    df = load_candidates_from_db('green_bond')
    if df.empty:
        return []
    filtered_df = df[df['fit_score'] >= min_fit_score]
    return filtered_df.to_dict('records')

# --- Main Run Block ---
if __name__ == '__main__':
    app.run(debug=True)
