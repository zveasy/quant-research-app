"""PPP deviation calculation."""

from __future__ import annotations
import pandas as pd


def _split_pair(pair: str) -> tuple[str, str]:
    if '/' in pair:
        base, quote = pair.split('/')
    else:
        base, quote = pair[:3], pair[3:]
    return base, quote


def ppp_deviation(df_fx: pd.DataFrame, df_cpi: pd.DataFrame) -> pd.DataFrame:
    """Calculate deviation from purchasing power parity.

    Parameters
    ----------
    df_fx : DataFrame
        Columns ``[date, pair, fx_rate]``.
    df_cpi : DataFrame
        Columns ``[date, country, cpi]``.

    Returns
    -------
    DataFrame
        Tidy with columns ``[date, pair, ppp_dev_pct]``.

    Examples
    --------
    >>> import pandas as pd
    >>> df_fx = pd.DataFrame({
    ...     'date': ['2020-01-01', '2020-01-02'],
    ...     'pair': ['EURUSD', 'EURUSD'],
    ...     'fx_rate': [1.1, 1.2],
    ... })
    >>> df_cpi = pd.DataFrame({
    ...     'date': ['2020-01-01','2020-01-02','2020-01-01','2020-01-02'],
    ...     'country': ['EUR','EUR','USD','USD'],
    ...     'cpi': [100,101,100,100.5],
    ... })
    >>> ppp_deviation(df_fx, df_cpi)
             date    pair  ppp_dev_pct
    0  2020-01-01  EURUSD    10.000000
    1  2020-01-02  EURUSD    20.694698
    """
    df_cpi = df_cpi.copy()
    df_cpi['rel'] = df_cpi.sort_values('date').groupby('country')['cpi'].transform(lambda x: x / x.iloc[0])

    base_quote = df_fx['pair'].apply(_split_pair)
    df_fx = df_fx.assign(base=base_quote.str[0], quote=base_quote.str[1])

    merged = df_fx.merge(df_cpi[['date','country','rel']], left_on=['date','base'], right_on=['date','country'])
    merged = merged.rename(columns={'rel':'rel_base'}).drop('country', axis=1)
    merged = merged.merge(df_cpi[['date','country','rel']], left_on=['date','quote'], right_on=['date','country'])
    merged = merged.rename(columns={'rel':'rel_quote'}).drop('country', axis=1)

    merged['implied'] = merged['rel_quote'] / merged['rel_base']
    merged['ppp_dev_pct'] = (merged['fx_rate'] / merged['implied'] - 1) * 100
    return merged[['date','pair','ppp_dev_pct']].sort_values(['pair','date']).reset_index(drop=True)
