import pandas as pd
from risk.stress import monte_carlo_stress, var95


def test_monte_carlo_shapes():
    df = pd.DataFrame({
        'A': [0.01, 0.02, -0.01],
        'B': [0.0, 0.01, 0.02],
    })
    paths = monte_carlo_stress(df, horizon=5, paths=100)
    assert paths.shape == (100, 5, 2)
    v = var95(paths)
    assert v.shape == (2,)
