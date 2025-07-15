"""Dash UI for scenario simulation."""

from __future__ import annotations

import io

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from risk.scenario_dsl import parse_yaml
from risk.gpu_engine import run_engine


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Textarea(id='yaml', style={'width': '100%', 'height': '300px'}),
                html.Button('Run', id='run-btn')
            ], width=4),
            dbc.Col([
                dcc.Graph(id='pnl'),
                html.Div(id='metrics'),
                html.A('Download CSV', id='download', href='', download='pnl.csv')
            ], width=8)
        ])
    ])

app.layout = layout()


@app.callback(
    dash.dependencies.Output('pnl', 'figure'),
    dash.dependencies.Output('metrics', 'children'),
    dash.dependencies.Output('download', 'href'),
    [dash.dependencies.Input('run-btn', 'n_clicks')],
    [dash.dependencies.State('yaml', 'value')],
)
def run_scenarios(n_clicks, yaml_text):
    if not n_clicks or not yaml_text:
        return {}, '', ''
    scenarios = parse_yaml(yaml_text)
    positions = pd.DataFrame({'pos': [1.0]})
    var, es, dist = run_engine(positions, scenarios)
    fig = px.histogram(dist.get(), nbins=50)
    csv = io.StringIO()
    pd.DataFrame({'pnl': dist.get()}).to_csv(csv, index=False)
    href = 'data:text/csv;base64,' + csv.getvalue().encode().decode('utf-8')
    metrics = f"VaR: {var:.2f}, ES: {es:.2f}"
    return fig, metrics, href


if __name__ == '__main__':
    app.run_server(debug=True)
