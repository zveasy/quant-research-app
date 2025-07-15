import pandas as pd
from factors.fx_ppp import ppp_deviation


def test_ppp_deviation_basic():
    df_fx = pd.DataFrame({
        'date': ['2020-01-01', '2020-01-02'],
        'pair': ['EURUSD', 'EURUSD'],
        'fx_rate': [1.1, 1.2],
    })
    df_cpi = pd.DataFrame({
        'date': ['2020-01-01','2020-01-02','2020-01-01','2020-01-02'],
        'country': ['EUR','EUR','USD','USD'],
        'cpi': [100,101,100,100.5],
    })
    result = ppp_deviation(df_fx, df_cpi)
    assert result.shape == (2, 3)
    assert result['ppp_dev_pct'].iloc[0] == 10.0
