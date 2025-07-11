import pandas as pd
from universe_scouter.currency_explorer import get_assets as get_currency_assets
from universe_scouter.carbon_credit_explorer import get_assets as get_carbon_assets
from universe_scouter.green_bond_explorer import get_assets as get_green_bond_assets


def _check_df(df: pd.DataFrame):
    assert not df.empty
    assert set(["symbol", "name"]).issubset(df.columns)


def test_currency_explorer():
    df = get_currency_assets()
    _check_df(df)


def test_carbon_credit_explorer():
    df = get_carbon_assets()
    _check_df(df)


def test_green_bond_explorer():
    df = get_green_bond_assets()
    _check_df(df)
