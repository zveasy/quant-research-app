"""Utilities for SHAP model explanations."""

from __future__ import annotations

import pandas as pd
import shap
from matplotlib import pyplot as plt


def explain_model(model, X_sample: pd.DataFrame) -> pd.DataFrame:
    """Return SHAP values for a LightGBM or XGBoost model.

    Parameters
    ----------
    model : object
        Trained LightGBM or XGBoost model supporting the ``predict`` API.
    X_sample : pandas.DataFrame
        Sample of input features.

    Returns
    -------
    pandas.DataFrame
        Table with ``feature``, ``shap_value`` and ``rank`` columns.
    """
    if hasattr(model, "booster"):
        # LightGBM
        explainer = shap.TreeExplainer(model.booster_ if hasattr(model, "booster_") else model)
    else:
        explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    if isinstance(shap_values, list):
        shap_values = shap_values[0]
    df = pd.DataFrame({
        "feature": X_sample.columns,
        "shap_value": shap_values.mean(axis=0),
    })
    df["rank"] = df.shap_value.abs().rank(ascending=False, method="dense").astype(int)
    return df.sort_values("rank")


def save_waterfall(path: str, shap_values, features, max_display: int = 10) -> None:
    """Save a SHAP waterfall plot."""
    plt.figure()
    shap.waterfall_plot(shap.Explanation(values=shap_values, feature_names=features))
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
