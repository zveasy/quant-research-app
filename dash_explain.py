"""Minimal Dash app for SHAP explanations."""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from explain.shap_utils import explain_model, save_waterfall

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Placeholder data
DATA = pd.DataFrame({"symbol": ["AAPL"], "date": ["2024-01-01"], "factor1": [0.1]})
MODEL = None

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("Explain Prediction"),
            dcc.Dropdown(id="symbol", options=[{"label": s, "value": s} for s in DATA.symbol.unique()]),
            dcc.DatePickerSingle(id="date", date=str(DATA.date.iloc[0])),
        ], width=3),
        dbc.Col([
            html.Img(id="force-plot"),
            html.Div(id="factor-table"),
        ], width=9),
    ])
], fluid=True)


@app.callback(
    Output("force-plot", "src"),
    Output("factor-table", "children"),
    Input("symbol", "value"),
    Input("date", "date"),
)
def update(symbol, date):
    if symbol is None or date is None or MODEL is None:
        return dash.no_update, dash.no_update
    row = DATA[(DATA.symbol == symbol) & (DATA.date == date)]
    if row.empty:
        return dash.no_update, dash.no_update
    df = explain_model(MODEL, row[[c for c in row.columns if c.startswith("factor")]])
    save_waterfall("/tmp/force.png", df.shap_value.values, df.feature.tolist())
    table = dbc.Table.from_dataframe(df.head(5))
    return dash.get_asset_url("force.png"), table


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
