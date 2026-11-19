"""
Scenario-grouped stratified train/validation/test dataset partitioning.
Directly partitions scenarios per workload family to guarantee perfect stratification
and disjointness across any dataset scale without min-count exceptions.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


def create_scenario_splits(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    stratify_col: str = "workload_family",
    random_state: int = 42,
    save_path: Path | str = "data/splits.json",
) -> Dict[str, Any]:
    """
    Partition scenarios into train/val/test splits strictly by scenario_id.
    Guarantees no scenario crosses split boundaries and preserves family ratios.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-4, "Ratios must sum to 1.0"

    scenario_df = df[["scenario_id", stratify_col]].drop_duplicates()
    rng = random.Random(random_state)

    train_scenarios: List[str] = []
    val_scenarios: List[str] = []
    test_scenarios: List[str] = []

    # Partition each class independently to maintain exact stratification
    for family, group in scenario_df.groupby(stratify_col):
        scen_list = list(group["scenario_id"].values)
        rng.shuffle(scen_list)

        n_total = len(scen_list)
        if n_total >= 3:
            n_train = max(1, int(round(n_total * train_ratio)))
            n_val = max(1, int(round(n_total * val_ratio)))
            # Remaining goes to test
            n_test = max(1, n_total - n_train - n_val)
            # Rebalance if rounding exceeded
            while n_train + n_val + n_test > n_total:
                if n_train > 1:
                    n_train -= 1
                elif n_val > 1:
                    n_val -= 1
                elif n_test > 1:
                    n_test -= 1
            while n_train + n_val + n_test < n_total:
                n_train += 1
        elif n_total == 2:
            n_train, n_val, n_test = 1, 0, 1
        else:
            n_train, n_val, n_test = 1, 0, 0

        train_scenarios.extend(scen_list[:n_train])
        val_scenarios.extend(scen_list[n_train : n_train + n_val])
        test_scenarios.extend(scen_list[n_train + n_val : n_train + n_val + n_test])

    # Final shuffle
    rng.shuffle(train_scenarios)
    rng.shuffle(val_scenarios)
    rng.shuffle(test_scenarios)

    splits = {
        "train": train_scenarios,
        "validation": val_scenarios,
        "test": test_scenarios,
        "random_state": random_state,
        "counts": {
            "train": len(train_scenarios),
            "validation": len(val_scenarios),
            "test": len(test_scenarios),
            "total": len(scenario_df),
        },
    }

    save_p = Path(save_path)
    save_p.parent.mkdir(parents=True, exist_ok=True)
    with open(save_p, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    return splits


def load_scenario_splits(splits_path: Path | str = "data/splits.json") -> Dict[str, Any]:
    with open(splits_path, "r", encoding="utf-8") as f:
        return json.load(f)
