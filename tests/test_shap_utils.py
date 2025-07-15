import sys
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

sys.path.append('.')
from explain.shap_utils import explain_model


def test_explain_model():
    X = np.random.rand(50, 5)
    y = np.random.rand(50)
    df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    model = XGBRegressor(n_estimators=10, max_depth=2, verbosity=0)
    model.fit(df, y)
    res = explain_model(model, df.iloc[:10])
    assert "feature" in res.columns
    assert len(res) == df.shape[1]
