import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class FactorPortfolioEnv(gym.Env):
    """A simple portfolio trading environment for reinforcement learning.

    Parameters
    ----------
    data_path : str
        Path to a Parquet file with columns ``date`` followed by factor
        columns and asset return columns. Asset return columns must be
        suffixed with ``_ret``.
    transaction_cost : float, optional
        Proportional transaction cost per unit weight change. Defaults
        to ``0.001`` (10 bps).

    Observation
    -----------
    ``ndarray`` of shape ``(num_factors + 1,)`` containing the latest
    factor scores and current cash position.

    Action
    ------
    Continuous weight vector over ``num_assets``. Components must sum to
    ``<=1``.

    Reward
    ------
    Daily portfolio return minus transaction costs.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'date': ['2024-01-01', '2024-01-02'],
    ...     'factor1': [0.1, 0.2],
    ...     'ret_A': [0.01, -0.02],
    ... })
    >>> _ = df.to_parquet('tmp.parquet')
    >>> env = FactorPortfolioEnv('tmp.parquet')
    >>> obs, _ = env.reset()
    >>> obs.shape
    (2,)
    >>> action = np.array([0.5], dtype=float)
    >>> obs, reward, terminated, truncated, _ = env.step(action)
    >>> terminated
    True
    """

    metadata = {"render.modes": []}

    def __init__(self, data_path: str, transaction_cost: float = 0.001):
        self.data = pd.read_parquet(data_path)
        self.factors = [c for c in self.data.columns if c not in ['date'] and not c.endswith('_ret')]
        self.assets = [c[:-4] for c in self.data.columns if c.endswith('_ret')]
        self.num_factors = len(self.factors)
        self.num_assets = len(self.assets)
        self.transaction_cost = transaction_cost
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.num_factors + 1,),
            dtype=np.float32,
        )
        self.action_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self.num_assets,),
            dtype=np.float32,
        )
        self._step = 0
        self.prev_weights = np.zeros(self.num_assets)

    def _get_obs(self):
        row = self.data.iloc[self._step]
        factors = row[self.factors].to_numpy(dtype=np.float32)
        cash = 1.0 - self.prev_weights.sum()
        return np.concatenate([factors, [cash]]).astype(np.float32)

    def reset(self, *, seed: int | None = None, options=None):
        super().reset(seed=seed)
        self._step = 0
        self.prev_weights = np.zeros(self.num_assets)
        observation = self._get_obs()
        info = {}
        return observation, info

    def step(self, action: np.ndarray):
        action = np.clip(action, 0.0, 1.0)
        total_weight = action.sum()
        if total_weight > 1.0:
            action = action / total_weight
        row = self.data.iloc[self._step]
        returns = row[[f"{a}_ret" for a in self.assets]].to_numpy(dtype=float)
        trade_cost = self.transaction_cost * np.sum(np.abs(action - self.prev_weights))
        portfolio_return = float(np.dot(action, returns))
        reward = portfolio_return - trade_cost
        self.prev_weights = action
        self._step += 1
        terminated = self._step >= len(self.data)
        truncated = False
        observation = self._get_obs() if not terminated else np.zeros(self.num_factors + 1, dtype=np.float32)
        info = {"portfolio_return": portfolio_return}
        return observation, reward, terminated, truncated, info
