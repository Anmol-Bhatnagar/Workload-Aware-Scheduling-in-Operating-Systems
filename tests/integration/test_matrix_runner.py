"""
Integration test for matrix runner and artifact persistence.
"""

from pathlib import Path
import tempfile
import pytest

from scheduling_lab.experiments.artifacts import ArtifactStore
from scheduling_lab.experiments.registry import ExperimentRegistry
from scheduling_lab.experiments.runner import ExperimentRunner
from scheduling_lab.workloads.generator import WorkloadGenerator


def test_mini_matrix_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        runs_dir = tmp_path / "runs"
        registry_file = runs_dir / "registry.json"

        artifact_store = ArtifactStore(base_dir=runs_dir)
        registry = ExperimentRegistry(registry_path=registry_file)

        runner = ExperimentRunner(artifact_store=artifact_store, registry=registry)

        # Generate 2 scenarios
        scen1 = WorkloadGenerator.generate_scenario(family="interactive", process_count=5, seed=1)
        scen2 = WorkloadGenerator.generate_scenario(family="cpu_bound", process_count=5, seed=2)

        results = runner.run_matrix([scen1, scen2])

        # 2 scenarios * 6 candidates = 12 runs
        assert len(results) == 12
        assert all(r["status"] == "COMPLETED" for r in results)

        # Verify artifacts exist for first run
        first_run_id = results[0]["run_id"]
        run_folder = runs_dir / first_run_id

        assert (run_folder / "run_manifest.json").exists()
        assert (run_folder / "scenario.json").exists()
        assert (run_folder / "event_trace.jsonl").exists()
        assert (run_folder / "timeline.csv").exists()
        assert (run_folder / "process_metrics.csv").exists()
        assert (run_folder / "summary_metrics.json").exists()
