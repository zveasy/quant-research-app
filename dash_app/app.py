import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
import numpy as np

# Load multi-stock data
df = pd.read_csv("sample_data/multi_stock.csv", index_col="Date", parse_dates=True)
returns = np.log(df / df.shift(1)).dropna()

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server  # for deployment

app.layout = html.Div([
    html.H1("PCA Dashboard"),
    dcc.Dropdown(
        id='n-components',
        options=[{'label': str(i), 'value': i} for i in range(1, min(len(returns.columns), 6))],
        value=2,
        clearable=False
    ),
    dcc.Graph(id='explained-variance'),
    dcc.Graph(id='pca-scatter')
])

@app.callback(
    Output('explained-variance', 'figure'),
    Output('pca-scatter', 'figure'),
    Input('n-components', 'value')
)
def update_pca(n):
    pca = PCA(n_components=n)
    X = pca.fit_transform(returns)

    fig1 = px.bar(
        x=[f"PC{i+1}" for i in range(n)],
        y=pca.explained_variance_ratio_,
        labels={'x': 'Principal Component', 'y': 'Explained Variance Ratio'},
        title="Explained Variance by Component"
    )

    fig2 = px.scatter(
        x=X[:, 0],
        y=X[:, 1] if n > 1 else [0]*len(X),
        labels={'x': 'PC1', 'y': 'PC2'},
        title="PCA Projection (PC1 vs PC2)"
    )

    return fig1, fig2

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)

