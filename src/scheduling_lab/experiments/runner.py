"""
CPU Experiment Matrix Runner.
Replays identical workload instances across candidate scheduling algorithms.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from scheduling_lab.core.simulator import CPUSimulator
from scheduling_lab.experiments.artifacts import ArtifactStore
from scheduling_lab.experiments.registry import ExperimentRegistry
from scheduling_lab.schedulers.registry import create_scheduler
from scheduling_lab.workloads.generator import WorkloadGenerator

logger = logging.getLogger(__name__)

DEFAULT_CANDIDATES = [
    {"id": "FCFS", "type": "fcfs", "params": {}},
    {"id": "SJF", "type": "sjf", "params": {}},
    {"id": "PRIORITY", "type": "priority", "params": {"lower_is_higher": True}},
    {"id": "RR_Q2", "type": "rr", "params": {"quantum": 2, "name": "RR_Q2"}},
    {"id": "RR_Q5", "type": "rr", "params": {"quantum": 5, "name": "RR_Q5"}},
    {"id": "RR_Q10", "type": "rr", "params": {"quantum": 10, "name": "RR_Q10"}},
]


class ExperimentRunner:
    """Executes controlled comparative experiments across scheduling policies."""

    def __init__(
        self,
        artifact_store: Optional[ArtifactStore] = None,
        registry: Optional[ExperimentRegistry] = None,
        candidates: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.artifacts = artifact_store or ArtifactStore()
        self.registry = registry or ExperimentRegistry()
        self.candidates = candidates or DEFAULT_CANDIDATES

    def run_scenario_matrix(
        self,
        scenario_data: Dict[str, Any],
        context_switch_cost: int = 0,
    ) -> List[Dict[str, Any]]:
        """Run all candidate policies against a single scenario instance."""
        scenario_id = scenario_data["scenario_id"]
        workload_family = scenario_data["workload_family"]
        seed = scenario_data.get("seed")

        processes = WorkloadGenerator.load_scenario_processes(scenario_data)
        results: List[Dict[str, Any]] = []

        for cand in self.candidates:
            cand_id = cand["id"]
            cand_type = cand["type"]
            cand_params = cand.get("params", {})

            run_id = f"cpu_{scenario_id}_{cand_id}"
            scheduler = create_scheduler(cand_type, **cand_params)
            sim = CPUSimulator(scheduler=scheduler, context_switch_cost=context_switch_cost)

            try:
                sim_result = sim.run(
                    process_workload=processes,
                    scenario_id=scenario_id,
                    seed=seed,
                    validate=True,
                )
                self.artifacts.save_run_artifacts(
                    run_id=run_id,
                    result=sim_result,
                    scenario_data=scenario_data,
                    extra_metadata={"candidate_id": cand_id},
                )
                reg_entry = self.registry.register_run(
                    run_id=run_id,
                    experiment_type="CPU",
                    scenario_id=scenario_id,
                    policy=cand_id,
                    workload_family=workload_family,
                    status="COMPLETED",
                    summary_metrics=sim_result.metrics.to_dict(),
                    auto_flush=False,
                )
                results.append(reg_entry)
            except Exception as exc:
                logger.error(f"Failed run {run_id}: {exc}", exc_info=True)
                reg_entry = self.registry.register_run(
                    run_id=run_id,
                    experiment_type="CPU",
                    scenario_id=scenario_id,
                    policy=cand_id,
                    workload_family=workload_family,
                    status="FAILED",
                    error_message=str(exc),
                    auto_flush=False,
                )
                results.append(reg_entry)

        return results

    def run_matrix(
        self,
        scenarios: List[Dict[str, Any]],
        context_switch_cost: int = 0,
    ) -> List[Dict[str, Any]]:
        """Execute matrix for all scenarios."""
        all_results: List[Dict[str, Any]] = []
        for scen in scenarios:
            res = self.run_scenario_matrix(scen, context_switch_cost=context_switch_cost)
            all_results.extend(res)
        # Flush registry once at the very end
        self.registry.flush()
        return all_results
