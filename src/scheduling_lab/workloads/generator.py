"""
Workload generator for synthetic CPU scheduling scenarios.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from scheduling_lab.core.models import Process
from scheduling_lab.workloads.profiles import (
    PROFILE_CONFIGS,
    WorkloadFamily,
    WorkloadProfileConfig,
)


class WorkloadGenerator:
    """Generates parameterized, reproducible synthetic workload scenarios."""

    @classmethod
    def generate_scenario(
        cls,
        family: WorkloadFamily | str,
        process_count: int = 10,
        seed: int = 42,
        scenario_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a complete workload scenario dictionary."""
        if isinstance(family, str):
            family = WorkloadFamily(family.lower())

        rng = random.Random(seed)
        scenario_id = scenario_id or f"{family.value}_s{seed}_n{process_count}"
        processes: List[Process] = []

        curr_arrival = 0
        config: WorkloadProfileConfig = PROFILE_CONFIGS[family]

        for i in range(process_count):
            pid = f"P{i + 1}"

            # Calculate arrival time
            if i > 0:
                if family == WorkloadFamily.BURSTY_ARRIVALS:
                    # In bursty arrival mode: 70% chance of arriving immediately in burst, 30% chance of a long pause
                    if rng.random() < config.burst_arrival_probability:
                        gap = rng.randint(0, 1)
                    else:
                        gap = rng.randint(10, 25)
                else:
                    gap = rng.randint(*config.arrival_gap_range)
                curr_arrival += gap

            # Determine burst profiles
            if family == WorkloadFamily.MIXED:
                # Sub-profile assignment: 40% CPU-bound, 40% IO-bound, 20% Interactive
                sub_r = rng.random()
                if sub_r < 0.40:
                    sub_cfg = PROFILE_CONFIGS[WorkloadFamily.CPU_BOUND]
                elif sub_r < 0.80:
                    sub_cfg = PROFILE_CONFIGS[WorkloadFamily.IO_BOUND]
                else:
                    sub_cfg = PROFILE_CONFIGS[WorkloadFamily.INTERACTIVE]
            else:
                sub_cfg = config

            burst_count = rng.randint(*sub_cfg.burst_count_range)
            cpu_bursts = [rng.randint(*sub_cfg.cpu_burst_range) for _ in range(burst_count)]

            # Number of IO bursts is burst_count - 1
            io_bursts: List[int] = []
            if burst_count > 1:
                io_bursts = [rng.randint(*sub_cfg.io_burst_range) for _ in range(burst_count - 1)]

            priority = rng.randint(*sub_cfg.priority_range)

            proc = Process(
                pid=pid,
                arrival_time=curr_arrival,
                priority=priority,
                cpu_bursts=cpu_bursts,
                io_bursts=io_bursts,
            )
            processes.append(proc)

        return {
            "scenario_id": scenario_id,
            "workload_family": family.value,
            "process_count": process_count,
            "seed": seed,
            "processes": [p.to_dict() for p in processes],
        }

    @classmethod
    def load_scenario_processes(cls, scenario_data: Dict[str, Any]) -> List[Process]:
        """Convert a scenario dictionary back into a list of Process objects."""
        return [
            Process(
                pid=p["pid"],
                arrival_time=p["arrival_time"],
                priority=p["priority"],
                cpu_bursts=list(p["cpu_bursts"]),
                io_bursts=list(p.get("io_bursts", [])),
            )
            for p in scenario_data["processes"]
        ]
