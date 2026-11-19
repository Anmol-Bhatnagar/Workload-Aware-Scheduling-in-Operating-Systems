"""
Composite cost objective function and within-scenario min-max normalization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np

DEFAULT_WEIGHTS = {
    "response_cost": 0.30,
    "waiting_cost": 0.25,
    "turnaround_cost": 0.20,
    "context_switch_cost": 0.15,
    "utilisation_cost": 0.10,
}

SENSITIVITY_WEIGHTS = {
    "response_cost": 0.40,
    "waiting_cost": 0.20,
    "turnaround_cost": 0.20,
    "context_switch_cost": 0.10,
    "utilisation_cost": 0.10,
}


def normalize_component(values: List[float], invert: bool = False) -> List[float]:
    """
    Min-max normalizes a metric within a single scenario across candidate policies.
    If all values are identical, returns neutral 0.5 for all candidates.
    If invert is True, higher input value maps to lower cost.
    """
    arr = np.array(values, dtype=float)
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    if np.isclose(min_val, max_val):
        return [0.5] * len(values)

    norm = (arr - min_val) / (max_val - min_val)
    if invert:
        norm = 1.0 - norm
    return [float(x) for x in norm]


def compute_scenario_costs(
    policy_metrics: Dict[str, Dict[str, Any]],
    weights: Dict[str, float] = DEFAULT_WEIGHTS,
) -> Dict[str, Dict[str, float]]:
    """
    Given candidate policies evaluated on the exact same scenario, compute within-scenario
    normalized component costs and composite cost for each policy.
    """
    policies = list(policy_metrics.keys())
    if not policies:
        return {}

    raw_response = [float(policy_metrics[p]["avg_response_time"]) for p in policies]
    raw_waiting = [float(policy_metrics[p]["avg_waiting_time"]) for p in policies]
    raw_turnaround = [float(policy_metrics[p]["avg_turnaround_time"]) for p in policies]
    raw_cs = [float(policy_metrics[p]["context_switches"]) for p in policies]
    # For CPU utilisation, higher is better, so invert when calculating cost
    raw_util = [float(policy_metrics[p]["cpu_utilisation_pct"]) for p in policies]

    norm_resp = normalize_component(raw_response, invert=False)
    norm_wait = normalize_component(raw_waiting, invert=False)
    norm_ta = normalize_component(raw_turnaround, invert=False)
    norm_cs = normalize_component(raw_cs, invert=False)
    norm_util_cost = normalize_component(raw_util, invert=True)

    result: Dict[str, Dict[str, float]] = {}
    for i, p in enumerate(policies):
        cost = (
            weights["response_cost"] * norm_resp[i]
            + weights["waiting_cost"] * norm_wait[i]
            + weights["turnaround_cost"] * norm_ta[i]
            + weights["context_switch_cost"] * norm_cs[i]
            + weights["utilisation_cost"] * norm_util_cost[i]
        )
        result[p] = {
            "response_cost": round(norm_resp[i], 4),
            "waiting_cost": round(norm_wait[i], 4),
            "turnaround_cost": round(norm_ta[i], 4),
            "context_switch_cost": round(norm_cs[i], 4),
            "utilisation_cost": round(norm_util_cost[i], 4),
            "composite_cost": round(cost, 6),
        }
    return result


def find_winning_policy(
    policy_metrics: Dict[str, Dict[str, Any]],
    weights: Dict[str, float] = DEFAULT_WEIGHTS,
) -> Tuple[str, float, Dict[str, Dict[str, float]]]:
    """Find the policy that achieves minimum composite cost for a scenario."""
    costs = compute_scenario_costs(policy_metrics, weights)
    # Deterministic tie-breaking by policy name if costs are equal
    winner = min(costs.keys(), key=lambda p: (costs[p]["composite_cost"], p))
    return winner, costs[winner]["composite_cost"], costs
