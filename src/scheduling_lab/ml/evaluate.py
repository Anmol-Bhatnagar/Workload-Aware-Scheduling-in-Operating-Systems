"""
Held-out test set evaluation and baseline comparisons.
Compares ML recommender against Always FCFS, Always RR_Q5, Best Fixed Policy, and Oracle.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from scheduling_lab.workloads.features import FEATURE_NAMES


class Evaluator:
    """Evaluates policy recommender against baselines on held-out scenarios."""

    @classmethod
    def find_best_fixed_policy(
        cls,
        df: pd.DataFrame,
        train_val_scenario_ids: List[str],
        candidate_policies: List[str] = ("FCFS", "SJF", "PRIORITY", "RR_Q2", "RR_Q5", "RR_Q10"),
    ) -> Tuple[str, float]:
        """Find the single fixed policy yielding lowest average cost on train/val data only."""
        subset = df[df["scenario_id"].isin(train_val_scenario_ids)]
        avg_costs = {pol: float(subset[f"cost_{pol}"].mean()) for pol in candidate_policies}
        best_pol = min(avg_costs.keys(), key=lambda p: avg_costs[p])
        return best_pol, avg_costs[best_pol]

    @classmethod
    def evaluate(
        cls,
        model: DecisionTreeClassifier,
        df: pd.DataFrame,
        test_scenario_ids: List[str],
        best_fixed_policy: str,
    ) -> Dict[str, Any]:
        test_df = df[df["scenario_id"].isin(test_scenario_ids)].copy()
        if test_df.empty:
            raise ValueError("Test set is empty for provided scenario IDs")

        X_test = test_df[FEATURE_NAMES].values
        y_true = test_df["target_policy"].values

        # Predictions
        y_pred = model.predict(X_test)
        test_df["pred_policy"] = y_pred

        # Compute cost for ML recommender on each scenario
        ml_costs: List[float] = []
        for _, row in test_df.iterrows():
            pred_p = row["pred_policy"]
            ml_costs.append(float(row[f"cost_{pred_p}"]))
        test_df["ml_cost"] = ml_costs

        fcfs_costs = test_df["cost_FCFS"].values
        rr5_costs = test_df["cost_RR_Q5"].values
        best_fixed_costs = test_df[f"cost_{best_fixed_policy}"].values
        oracle_costs = test_df["target_cost"].values

        # Accuracy
        acc = float(np.mean(y_pred == y_true))

        # Average costs
        avg_ml = float(np.mean(ml_costs))
        avg_fcfs = float(np.mean(fcfs_costs))
        avg_rr5 = float(np.mean(rr5_costs))
        avg_best_fixed = float(np.mean(best_fixed_costs))
        avg_oracle = float(np.mean(oracle_costs))

        # Regret vs Oracle: (cost - oracle) / (oracle + 1e-6)
        regret_ml = float(np.mean((ml_costs - oracle_costs) / (oracle_costs + 1e-6)))
        regret_fcfs = float(np.mean((fcfs_costs - oracle_costs) / (oracle_costs + 1e-6)))
        regret_rr5 = float(np.mean((rr5_costs - oracle_costs) / (oracle_costs + 1e-6)))
        regret_best_fixed = float(np.mean((best_fixed_costs - oracle_costs) / (oracle_costs + 1e-6)))

        # Head-to-head comparisons
        ml_better_than_rr5 = float(np.mean(ml_costs < rr5_costs))
        ml_better_than_fcfs = float(np.mean(ml_costs < fcfs_costs))
        best_fixed_better_than_ml = float(np.mean(best_fixed_costs < ml_costs))

        # Breakdown by workload family
        family_breakdown: Dict[str, Dict[str, float]] = {}
        for fam, grp in test_df.groupby("workload_family"):
            fam_ml = float(grp["ml_cost"].mean())
            fam_rr5 = float(grp["cost_RR_Q5"].mean())
            fam_fcfs = float(grp["cost_FCFS"].mean())
            fam_bf = float(grp[f"cost_{best_fixed_policy}"].mean())
            fam_ora = float(grp["target_cost"].mean())
            family_breakdown[str(fam)] = {
                "ml_avg_cost": round(fam_ml, 4),
                "rr5_avg_cost": round(fam_rr5, 4),
                "fcfs_avg_cost": round(fam_fcfs, 4),
                "best_fixed_avg_cost": round(fam_bf, 4),
                "oracle_avg_cost": round(fam_ora, 4),
                "sample_count": len(grp),
            }

        # Bootstrap 95% CI for difference: (RR_Q5 cost - ML cost)
        # Positive diff means ML has lower cost (better)
        diff_rr5 = rr5_costs - ml_costs
        rng = np.random.RandomState(42)
        boot_diffs = []
        for _ in range(1000):
            sample = rng.choice(diff_rr5, size=len(diff_rr5), replace=True)
            boot_diffs.append(float(np.mean(sample)))
        ci_lower = float(np.percentile(boot_diffs, 2.5))
        ci_upper = float(np.percentile(boot_diffs, 97.5))

        evaluation_results = {
            "test_sample_count": len(test_df),
            "best_fixed_policy": best_fixed_policy,
            "policy_accuracy": round(acc, 4),
            "average_composite_costs": {
                "ML_Recommender": round(avg_ml, 4),
                "Always_FCFS": round(avg_fcfs, 4),
                "Always_RR_Q5": round(avg_rr5, 4),
                f"Best_Fixed_{best_fixed_policy}": round(avg_best_fixed, 4),
                "Per_Scenario_Oracle": round(avg_oracle, 4),
            },
            "average_regret_vs_oracle": {
                "ML_Recommender": round(regret_ml, 4),
                "Always_FCFS": round(regret_fcfs, 4),
                "Always_RR_Q5": round(regret_rr5, 4),
                f"Best_Fixed_{best_fixed_policy}": round(regret_best_fixed, 4),
            },
            "head_to_head_ratios": {
                "ml_beats_rr5": round(ml_better_than_rr5, 4),
                "ml_beats_fcfs": round(ml_better_than_fcfs, 4),
                "best_fixed_beats_ml": round(best_fixed_better_than_ml, 4),
            },
            "bootstrap_ci_rr5_minus_ml_cost": {
                "mean_diff": round(float(np.mean(diff_rr5)), 4),
                "ci_2_5": round(ci_lower, 4),
                "ci_97_5": round(ci_upper, 4),
            },
            "family_breakdown": family_breakdown,
        }
        return evaluation_results
