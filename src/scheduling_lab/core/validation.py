"""
Validation and assertion checks for simulator correctness.
"""

from __future__ import annotations

from typing import List

from scheduling_lab.core.models import Process, ProcessState
from scheduling_lab.core.metrics import SimulationMetrics


def validate_simulation_correctness(
    processes: List[Process],
    metrics: SimulationMetrics,
) -> None:
    """
    Validate conservation laws, timing invariants, and process termination.
    Raises AssertionError if any invariant is violated.
    """
    # 1. Termination check
    for p in processes:
        if p.state != ProcessState.TERMINATED:
            raise AssertionError(f"Process {p.pid} did not terminate (state={p.state})")
        if p.completion_time is None:
            raise AssertionError(f"Process {p.pid} completed without completion_time")
        if p.first_start_time is None:
            raise AssertionError(f"Process {p.pid} completed without first_start_time")

    # 2. Timing ordering invariants: turnaround >= response >= 0
    for p in processes:
        assert p.first_start_time is not None
        assert p.completion_time is not None
        assert p.first_start_time >= p.arrival_time, (
            f"Process {p.pid}: first_start ({p.first_start_time}) < arrival ({p.arrival_time})"
        )
        assert p.completion_time >= p.first_start_time, (
            f"Process {p.pid}: completion ({p.completion_time}) < first_start ({p.first_start_time})"
        )
        tt = p.completion_time - p.arrival_time
        rt = p.first_start_time - p.arrival_time
        assert tt >= rt >= 0, f"Process {p.pid}: turnaround ({tt}) < response ({rt})"

    # 3. CPU Conservation check: sum of CPU bursts == total CPU busy time
    total_expected_cpu = sum(p.total_expected_cpu for p in processes)
    total_executed_cpu = sum(p.total_cpu_time for p in processes)
    assert total_expected_cpu == total_executed_cpu, (
        f"CPU conservation violation: expected {total_expected_cpu} ticks, executed {total_executed_cpu}"
    )
    assert metrics.total_cpu_busy == total_executed_cpu, (
        f"Metrics CPU busy ({metrics.total_cpu_busy}) != executed CPU ({total_executed_cpu})"
    )

    # 4. Total lifetime consistency
    # For single CPU non-overlapping: turnaround = cpu_time + blocked_time + ready_wait
    for p in processes:
        assert p.completion_time is not None
        tt = p.completion_time - p.arrival_time
        accounted_time = p.total_cpu_time + p.total_blocked_time + p.total_ready_wait
        assert tt == accounted_time, (
            f"Process {p.pid}: turnaround ({tt}) != accounted time ({accounted_time}: "
            f"CPU={p.total_cpu_time}, Blocked={p.total_blocked_time}, Wait={p.total_ready_wait})"
        )
