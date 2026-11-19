"""
Workload profiles and parameter distributions for synthetic workload generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class WorkloadFamily(str, Enum):
    CPU_BOUND = "cpu_bound"
    IO_BOUND = "io_bound"
    INTERACTIVE = "interactive"
    MIXED = "mixed"
    BURSTY_ARRIVALS = "bursty_arrivals"


@dataclass(frozen=True)
class WorkloadProfileConfig:
    family: WorkloadFamily
    cpu_burst_range: Tuple[int, int]
    io_burst_range: Tuple[int, int]
    burst_count_range: Tuple[int, int]
    arrival_gap_range: Tuple[int, int]
    priority_range: Tuple[int, int]
    burst_arrival_probability: float = 0.0  # Probability of clustered batch arrivals


PROFILE_CONFIGS = {
    WorkloadFamily.CPU_BOUND: WorkloadProfileConfig(
        family=WorkloadFamily.CPU_BOUND,
        cpu_burst_range=(15, 40),
        io_burst_range=(0, 2),
        burst_count_range=(1, 2),
        arrival_gap_range=(1, 4),
        priority_range=(1, 5),
    ),
    WorkloadFamily.IO_BOUND: WorkloadProfileConfig(
        family=WorkloadFamily.IO_BOUND,
        cpu_burst_range=(1, 4),
        io_burst_range=(8, 20),
        burst_count_range=(3, 6),
        arrival_gap_range=(1, 3),
        priority_range=(1, 5),
    ),
    WorkloadFamily.INTERACTIVE: WorkloadProfileConfig(
        family=WorkloadFamily.INTERACTIVE,
        cpu_burst_range=(1, 3),
        io_burst_range=(3, 8),
        burst_count_range=(2, 4),
        arrival_gap_range=(0, 2),
        priority_range=(1, 3),
    ),
    WorkloadFamily.MIXED: WorkloadProfileConfig(
        family=WorkloadFamily.MIXED,
        cpu_burst_range=(2, 25),
        io_burst_range=(1, 12),
        burst_count_range=(1, 5),
        arrival_gap_range=(1, 5),
        priority_range=(1, 5),
    ),
    WorkloadFamily.BURSTY_ARRIVALS: WorkloadProfileConfig(
        family=WorkloadFamily.BURSTY_ARRIVALS,
        cpu_burst_range=(3, 20),
        io_burst_range=(1, 10),
        burst_count_range=(1, 4),
        arrival_gap_range=(0, 1),
        priority_range=(1, 5),
        burst_arrival_probability=0.7,
    ),
}
