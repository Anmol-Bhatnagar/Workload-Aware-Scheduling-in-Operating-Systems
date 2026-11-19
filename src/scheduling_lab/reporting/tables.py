"""
Summary tables and formatting utilities for simulation results.
"""

from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd


def format_metrics_comparison_table(
    candidate_metrics: Dict[str, Dict[str, Any]],
    composite_costs: Dict[str, Dict[str, float]],
) -> pd.DataFrame:
    """Format multiple policy runs into a structured comparison table with explicit units."""
    rows = []
    for pol_id, m in candidate_metrics.items():
        cost_info = composite_costs.get(pol_id, {})
        rows.append({
            "Policy / Config": pol_id,
            "Avg Response (ticks)": round(m.get("avg_response_time", 0), 2),
            "Avg Wait (ticks)": round(m.get("avg_waiting_time", 0), 2),
            "Avg Turnaround (ticks)": round(m.get("avg_turnaround_time", 0), 2),
            "Context Switches": int(m.get("context_switches", 0)),
            "CPU Util (%)": f"{m.get('cpu_utilisation_pct', 0):.1f}%",
            "Throughput (p/tick)": round(m.get("throughput", 0), 4),
            "Composite Cost": round(cost_info.get("composite_cost", 0.0), 4),
        })
    df = pd.DataFrame(rows)
    return df.sort_values(by="Composite Cost", ascending=True).reset_index(drop=True)


def format_process_details_table(process_metrics: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format per-process lifecycle table."""
    df = pd.DataFrame(process_metrics)
    rename_map = {
        "pid": "PID",
        "arrival_time": "Arrival (t)",
        "first_start_time": "First Start (t)",
        "completion_time": "Finish (t)",
        "total_cpu_time": "CPU Time (t)",
        "ready_wait_time": "Ready Wait (t)",
        "blocked_time": "Blocked (t)",
        "response_time": "Response (t)",
        "turnaround_time": "Turnaround (t)",
        "dispatch_count": "Dispatches",
    }
    present = {k: v for k, v in rename_map.items() if k in df.columns}
    return df[list(present.keys())].rename(columns=present)
