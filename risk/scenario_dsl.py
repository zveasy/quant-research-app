"""Simple scenario DSL parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

import yaml


@dataclass
class Scenario:
    name: str
    shocks: List[Callable[[float], float]]


def parse_yaml(text: str) -> List[Scenario]:
    data = yaml.safe_load(text)
    scenarios = []
    for item in data.get("scenarios", []):
        funcs = []
        if "shift_curves" in item:
            val = item["shift_curves"]
            funcs.append(lambda x, shift=val: x + shift)
        if "vol_spike" in item:
            mult = item["vol_spike"]
            funcs.append(lambda x, m=mult: x * m)
        if "fx_move" in item:
            fx = item["fx_move"]
            funcs.append(lambda x, f=fx: x * f)
        scenarios.append(Scenario(name=item.get("name", "scenario"), shocks=funcs))
    return scenarios
