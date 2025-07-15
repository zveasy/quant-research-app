from __future__ import annotations

import numpy as np
from gymnasium import spaces
from pettingzoo.utils import ParallelEnv


class MultiAgentOrderBook(ParallelEnv):
    """Simple order book environment for multiple agents."""

    metadata = {"render_modes": []}

    def __init__(self, n_agents: int = 2, episode_length: int = 50, base_price: float = 100.0):
        self.n_agents = n_agents
        self.possible_agents = [f"agent_{i}" for i in range(n_agents)]
        self.agents = self.possible_agents[:]
        self.episode_length = episode_length
        self.base_price = base_price
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(12,), dtype=np.float32)
        self.inventory = {a: 0 for a in self.agents}
        self.step_count = 0
        self._reset_book()

    def _reset_book(self) -> None:
        levels = np.linspace(self.base_price - 0.5, self.base_price + 0.5, 10)
        self.book = {
            "bids": levels[:5][::-1],
            "asks": levels[5:],
        }

    def _get_obs(self, agent: str) -> np.ndarray:
        time_left = (self.episode_length - self.step_count) / self.episode_length
        inv = self.inventory[agent]
        return np.concatenate([self.book["bids"], self.book["asks"], [time_left, inv]]).astype(np.float32)

    def reset(self, *, seed: int | None = None, options=None):
        super().reset(seed=seed)
        self.agents = self.possible_agents[:]
        self.inventory = {a: 0 for a in self.agents}
        self.step_count = 0
        self._reset_book()
        observations = {a: self._get_obs(a) for a in self.agents}
        infos = {a: {} for a in self.agents}
        return observations, infos

    def step(self, actions: dict[str, int]):
        observations, rewards, terminations, truncations, infos = {}, {}, {}, {}, {}
        self.step_count += 1
        mid = (self.book["bids"][0] + self.book["asks"][0]) / 2
        for agent, act in actions.items():
            if agent not in self.agents:
                continue
            order = [-1, 0, 1][act]
            if order == 1:  # buy
                exec_price = self.book["asks"][0]
                slippage = exec_price - mid
                self.inventory[agent] += 100
            elif order == -1:  # sell
                exec_price = self.book["bids"][0]
                slippage = mid - exec_price
                self.inventory[agent] -= 100
            else:
                slippage = 0.0
            inventory_cost = 0.001 * abs(self.inventory[agent])
            rewards[agent] = -(slippage + inventory_cost)
            terminations[agent] = self.step_count >= self.episode_length
            truncations[agent] = False
            infos[agent] = {}
            observations[agent] = self._get_obs(agent)
        if self.step_count >= self.episode_length:
            self.agents = []
        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass
