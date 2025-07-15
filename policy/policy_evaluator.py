from __future__ import annotations

import json
import os
from typing import Any, Dict

import grpc
import yaml
import jsonschema
import redis

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "policy_dsl_schema.yaml")


def load_policy(path: str) -> Dict[str, Any]:
    with open(SCHEMA_PATH) as f:
        schema = yaml.safe_load(f)
    with open(path) as f:
        policy = yaml.safe_load(f)
    jsonschema.validate(policy, schema)
    return policy


def check_action(action: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    if action.get("drawdown_pct", 0) > policy["max_drawdown_pct"]:
        return False
    if action.get("notional", 0) > policy["max_notional"]:
        return False
    hour = action.get("hour")
    if policy.get("allowed_hours") and hour not in policy["allowed_hours"]:
        return False
    if action.get("symbol") in policy.get("banned_symbols", []):
        return False
    return True


class PolicyInterceptor(grpc.ServerInterceptor):
    def __init__(self, policy_path: str, redis_url: str = "redis://localhost:6379"):
        self.policy = load_policy(policy_path)
        self.redis = redis.from_url(redis_url)

    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)

        def wrapper(request, context):
            action = json.loads(request.action_json) if hasattr(request, "action_json") else {}
            if not check_action(action, self.policy):
                self.redis.xadd("policy-violations", {"action": json.dumps(action)})
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "policy violation")
            return handler(request, context)

        return grpc.unary_unary_rpc_method_handler(wrapper)
