from __future__ import annotations

import os
import yaml
import boto3
from ray import init, shutdown
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv

from env_multi import MultiAgentOrderBook


def load_params(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main(config_yaml: str) -> None:
    params = load_params(config_yaml)
    init(ignore_reinit_error=True)
    env_creator = lambda cfg=None: ParallelPettingZooEnv(MultiAgentOrderBook())
    cfg = PPOConfig().environment(env_creator)
    cfg = cfg.rollouts(num_rollout_workers=params.get("num_workers", 0))
    cfg = cfg.training(**params.get("training", {}))
    algo = cfg.build()
    best_reward = float("-inf")
    best_ckpt = None
    while True:
        result = algo.train()
        if result["episode_reward_mean"] > best_reward:
            best_reward = result["episode_reward_mean"]
            best_ckpt = algo.save()
        if best_reward > 0:
            break
    if best_ckpt and os.environ.get("S3_PATH"):
        bucket, key = os.environ["S3_PATH"][5:].split("/", 1)
        boto3.client("s3").upload_file(best_ckpt, bucket, key)
    shutdown()


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
