"""
Experiment registry for tracking, filtering, and indexing all benchmark runs.
Features in-memory caching and batched flushing for maximum I/O performance.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExperimentRegistry:
    """Maintains an index of all executed experiments in results/runs/registry.json."""

    def __init__(self, registry_path: Path | str = "results/runs/registry.json") -> None:
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._dirty = False
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    for r in records:
                        self._cache[r["run_id"]] = r
            except Exception:
                self._cache = {}

    def flush(self) -> None:
        """Write all cached registry entries to disk."""
        if not self._dirty and self.registry_path.exists():
            return
        records = list(self._cache.values())
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        self._dirty = False

    def register_run(
        self,
        run_id: str,
        experiment_type: str,
        scenario_id: str,
        policy: str,
        workload_family: str,
        status: str = "COMPLETED",
        summary_metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        auto_flush: bool = True,
    ) -> Dict[str, Any]:
        """Add or update a run entry in the experiment registry."""
        now_iso = datetime.now(timezone.utc).isoformat()
        entry = {
            "run_id": run_id,
            "timestamp": now_iso,
            "experiment_type": experiment_type,
            "scenario_id": scenario_id,
            "policy": policy,
            "workload_family": workload_family,
            "status": status,
            "summary_metrics": summary_metrics or {},
            "error_message": error_message,
            "extra": extra or {},
        }
        self._cache[run_id] = entry
        self._dirty = True

        if auto_flush:
            self.flush()

        return entry

    def register_runs_batch(self, entries: List[Dict[str, Any]]) -> None:
        """Batch register multiple runs and flush once."""
        for e in entries:
            self._cache[e["run_id"]] = e
            self._dirty = True
        self.flush()

    def get_runs(
        self,
        experiment_type: Optional[str] = None,
        policy: Optional[str] = None,
        workload_family: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve runs matching filter conditions."""
        records = list(self._cache.values())
        filtered = records
        if experiment_type:
            filtered = [r for r in filtered if r.get("experiment_type") == experiment_type]
        if policy:
            filtered = [r for r in filtered if r.get("policy") == policy]
        if workload_family:
            filtered = [r for r in filtered if r.get("workload_family") == workload_family]
        if status:
            filtered = [r for r in filtered if r.get("status") == status]
        return filtered

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(run_id)
