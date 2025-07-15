import sys
import numpy as np
import pandas as pd

sys.path.append('.')
from rl_env import FactorPortfolioEnv


def test_env_step():
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'factor1': [0.1, 0.2],
        'A_ret': [0.01, -0.02],
    })
    path = 'tmp_env.parquet'
    df.to_parquet(path)
    env = FactorPortfolioEnv(path)
    obs, _ = env.reset()
    assert obs.shape[0] == 2
    action = np.array([0.5])
    obs, reward, term, trunc, _ = env.step(action)
    assert term is False
