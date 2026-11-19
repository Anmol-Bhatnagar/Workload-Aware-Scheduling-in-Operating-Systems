"""
ML dataset builder from experiment runs.
Constructs scenario-level feature tables and composite cost training labels.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from scheduling_lab.experiments.registry import ExperimentRegistry
from scheduling_lab.ml.objective import DEFAULT_WEIGHTS, find_winning_policy
from scheduling_lab.workloads.features import FEATURE_NAMES, PreExecutionFeatureExtractor
from scheduling_lab.workloads.generator import WorkloadGenerator


class DatasetBuilder:
    """Builds scenario-level tabular datasets from baseline experiment results."""

    def __init__(
        self,
        runs_dir: Path | str = "results/runs",
        registry: Optional[ExperimentRegistry] = None,
    ) -> None:
        self.runs_dir = Path(runs_dir)
        self.registry = registry or ExperimentRegistry(registry_path=self.runs_dir / "registry.json")

    def build_dataset(
        self,
        weights: Dict[str, float] = DEFAULT_WEIGHTS,
        required_candidates: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        required = required_candidates or ["FCFS", "SJF", "PRIORITY", "RR_Q2", "RR_Q5", "RR_Q10"]
        all_runs = self.registry.get_runs(experiment_type="CPU", status="COMPLETED")

        # Group runs by scenario_id
        runs_by_scenario: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for r in all_runs:
            s_id = r["scenario_id"]
            pol = r["policy"]
            if s_id not in runs_by_scenario:
                runs_by_scenario[s_id] = {}
            runs_by_scenario[s_id][pol] = r

        rows: List[Dict[str, Any]] = []

        for scenario_id, policy_runs in runs_by_scenario.items():
            # Verify all required candidates exist for this scenario
            if not all(cand in policy_runs for cand in required):
                continue

            # Load scenario definition to extract pre-execution features
            first_run_id = policy_runs[required[0]]["run_id"]
            scenario_file = self.runs_dir / first_run_id / "scenario.json"
            if not scenario_file.exists():
                continue

            with open(scenario_file, "r", encoding="utf-8") as f:
                scenario_data = json.load(f)

            workload_family = scenario_data.get("workload_family", "unknown")
            processes = WorkloadGenerator.load_scenario_processes(scenario_data)
            features = PreExecutionFeatureExtractor.extract_features(processes)

            # Extract metrics dictionary per candidate
            policy_metrics: Dict[str, Dict[str, Any]] = {
                cand: policy_runs[cand]["summary_metrics"] for cand in required
            }

            winner, min_cost, costs_by_policy = find_winning_policy(policy_metrics, weights=weights)

            row: Dict[str, Any] = {
                "scenario_id": scenario_id,
                "workload_family": workload_family,
                **features,
                "target_policy": winner,
                "target_cost": min_cost,
            }

            for cand in required:
                row[f"cost_{cand}"] = costs_by_policy[cand]["composite_cost"]
                row[f"resp_{cand}"] = policy_metrics[cand]["avg_response_time"]
                row[f"wait_{cand}"] = policy_metrics[cand]["avg_waiting_time"]
                row[f"ta_{cand}"] = policy_metrics[cand]["avg_turnaround_time"]
                row[f"cs_{cand}"] = policy_metrics[cand]["context_switches"]
                row[f"util_{cand}"] = policy_metrics[cand]["cpu_utilisation_pct"]

            rows.append(row)

        df = pd.DataFrame(rows)
        return df
