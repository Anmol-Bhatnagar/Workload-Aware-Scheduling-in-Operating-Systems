"""
Report Export CLI script.
Generates publication summary tables, markdown report drafts, and verified metrics.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from scheduling_lab.experiments.registry import ExperimentRegistry


def main() -> int:
    registry = ExperimentRegistry()
    runs = registry.get_runs()

    tables_dir = Path("results/tables")
    tables_dir.mkdir(parents=True, exist_ok=True)

    print(f"Total benchmark runs in registry: {len(runs)}")

    # 1. Summary by Policy across all CPU runs
    cpu_runs = [r for r in runs if r.get("experiment_type") == "CPU" and r.get("status") == "COMPLETED"]
    if cpu_runs:
        policy_data = []
        for r in cpu_runs:
            m = r.get("summary_metrics", {})
            policy_data.append({
                "policy": r.get("policy"),
                "family": r.get("workload_family"),
                "avg_response_time": m.get("avg_response_time"),
                "avg_waiting_time": m.get("avg_waiting_time"),
                "avg_turnaround_time": m.get("avg_turnaround_time"),
                "context_switches": m.get("context_switches"),
                "cpu_utilisation_pct": m.get("cpu_utilisation_pct"),
            })
        df_cpu = pd.DataFrame(policy_data)
        summary_by_pol = df_cpu.groupby("policy").mean(numeric_only=True).round(2).reset_index()
        summary_by_pol.to_csv(tables_dir / "cpu_policy_summary.csv", index=False)
        print("\n=== CPU Policy Aggregate Performance ===")
        print(summary_by_pol.to_string(index=False))

    # 2. Check ML evaluation
    eval_file = tables_dir / "ml_evaluation_test.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        print("\n=== Held-Out Test Evaluation ===")
        print(f"Test Accuracy: {eval_data.get('policy_accuracy') * 100:.1f}%")
        print("Composite Costs:", eval_data.get("average_composite_costs"))
        print(f"ML beats RR_Q5 in: {eval_data.get('head_to_head_ratios', {}).get('ml_beats_rr5') * 100:.1f}% of scenarios")

    return 0


if __name__ == "__main__":
    main()
