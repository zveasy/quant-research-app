"""Train PPO on FactorPortfolioEnv with MLflow logging."""

from __future__ import annotations

import argparse

import gymnasium as gym
import mlflow
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback

from rl_env import FactorPortfolioEnv


def main(path: str, eval_path: str | None = None):
    env = FactorPortfolioEnv(path)
    eval_env = FactorPortfolioEnv(eval_path or path)
    with mlflow.start_run():
        model = PPO("MlpPolicy", env, learning_rate=3e-4, gamma=0.99, verbose=0)
        callback = EvalCallback(eval_env, best_model_save_path="./best_model", log_path="./logs", eval_freq=1000)
        model.learn(total_timesteps=10000, callback=callback)
        mlflow.log_param("learning_rate", 3e-4)
        mlflow.log_param("gamma", 0.99)
        mlflow.log_artifact("./best_model/best_model.zip")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--eval")
    args = parser.parse_args()
    main(args.train, args.eval)
