"""
Artifact storage for experiment runs.
Guarantees immutable, per-run artifact directory generation with full reproducibility trails.
"""

from __future__ import annotations

import csv
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from scheduling_lab.core.simulator import SimulationResult


class ArtifactStore:
    """Manages saving and loading experiment artifacts in results/runs/<run_id>/."""

    def __init__(self, base_dir: Path | str = "results/runs") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_run_artifacts(
        self,
        run_id: str,
        result: SimulationResult,
        scenario_data: Dict[str, Any],
        config_hash: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Save complete suite of artifacts for a CPU simulation run."""
        run_dir = self.base_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # 1. run_manifest.json
        manifest = {
            "run_id": run_id,
            "timestamp": scenario_data.get("timestamp"),
            "scenario_id": result.scenario_id,
            "workload_family": scenario_data.get("workload_family"),
            "policy": result.scheduler_name,
            "seed": result.seed,
            "process_count": len(result.processes),
            "config_hash": config_hash,
            "python_version": sys.version,
            "platform": platform.platform(),
            "status": "COMPLETED",
            "extra": extra_metadata or {},
        }
        with open(run_dir / "run_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 2. scenario.json
        with open(run_dir / "scenario.json", "w", encoding="utf-8") as f:
            json.dump(scenario_data, f, indent=2)

        # 3. event_trace.jsonl
        with open(run_dir / "event_trace.jsonl", "w", encoding="utf-8") as f:
            for ev in result.events:
                f.write(json.dumps(ev.to_dict()) + "\n")

        # 4. timeline.csv
        with open(run_dir / "timeline.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["pid", "start_time", "end_time", "duration", "interval_type"])
            for item in result.timeline:
                writer.writerow([item.pid, item.start_time, item.end_time, item.duration, item.interval_type])

        # 5. process_metrics.csv
        with open(run_dir / "process_metrics.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "pid",
                "arrival_time",
                "first_start_time",
                "completion_time",
                "total_cpu_time",
                "ready_wait_time",
                "blocked_time",
                "response_time",
                "turnaround_time",
                "dispatch_count",
            ])
            for pm in result.metrics.per_process:
                writer.writerow([
                    pm.pid,
                    pm.arrival_time,
                    pm.first_start_time,
                    pm.completion_time,
                    pm.total_cpu_time,
                    pm.ready_wait_time,
                    pm.blocked_time,
                    pm.response_time,
                    pm.turnaround_time,
                    pm.dispatch_count,
                ])

        # 6. summary_metrics.json
        with open(run_dir / "summary_metrics.json", "w", encoding="utf-8") as f:
            json.dump(result.metrics.to_dict(), f, indent=2)

        return run_dir

    def load_run_summary(self, run_id: str) -> Optional[Dict[str, Any]]:
        manifest_path = self.base_dir / run_id / "run_manifest.json"
        summary_path = self.base_dir / run_id / "summary_metrics.json"

        if not manifest_path.exists() or not summary_path.exists():
            return None

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        return {**manifest, "metrics": summary}
