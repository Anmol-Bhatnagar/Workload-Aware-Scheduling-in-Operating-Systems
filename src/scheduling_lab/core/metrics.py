"""
Simulation metric calculation and validation.
Calculated directly from process life-cycle records and event traces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np

from scheduling_lab.core.models import Process, TimelineInterval


@dataclass
class ProcessMetricSummary:
    pid: str
    arrival_time: int
    first_start_time: int
    completion_time: int
    total_cpu_time: int
    ready_wait_time: int
    blocked_time: int
    response_time: int
    turnaround_time: int
    dispatch_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "first_start_time": self.first_start_time,
            "completion_time": self.completion_time,
            "total_cpu_time": self.total_cpu_time,
            "ready_wait_time": self.ready_wait_time,
            "blocked_time": self.blocked_time,
            "response_time": self.response_time,
            "turnaround_time": self.turnaround_time,
            "dispatch_count": self.dispatch_count,
        }


@dataclass
class SimulationMetrics:
    makespan: int
    total_cpu_busy: int
    total_idle_time: int
    cpu_utilisation_pct: float
    throughput: float
    context_switches: int
    avg_turnaround_time: float
    std_turnaround_time: float
    avg_response_time: float
    std_response_time: float
    p95_response_time: float
    avg_waiting_time: float
    std_waiting_time: float
    max_waiting_time: int
    per_process: List[ProcessMetricSummary]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "makespan": self.makespan,
            "total_cpu_busy": self.total_cpu_busy,
            "total_idle_time": self.total_idle_time,
            "cpu_utilisation_pct": round(self.cpu_utilisation_pct, 4),
            "throughput": round(self.throughput, 6),
            "context_switches": self.context_switches,
            "avg_turnaround_time": round(self.avg_turnaround_time, 4),
            "std_turnaround_time": round(self.std_turnaround_time, 4),
            "avg_response_time": round(self.avg_response_time, 4),
            "std_response_time": round(self.std_response_time, 4),
            "p95_response_time": round(self.p95_response_time, 4),
            "avg_waiting_time": round(self.avg_waiting_time, 4),
            "std_waiting_time": round(self.std_waiting_time, 4),
            "max_waiting_time": self.max_waiting_time,
            "per_process": [p.to_dict() for p in self.per_process],
        }


def calculate_metrics(
    processes: List[Process],
    timeline: List[TimelineInterval],
    context_switches: int,
    makespan: int,
) -> SimulationMetrics:
    """Calculate aggregate and per-process metrics accurately from simulation outputs."""
    if not processes:
        raise ValueError("Cannot calculate metrics on empty process list")

    per_process: List[ProcessMetricSummary] = []
    turnarounds: List[int] = []
    responses: List[int] = []
    waitings: List[int] = []

    total_cpu_busy = 0

    for p in processes:
        if p.completion_time is None or p.first_start_time is None:
            raise ValueError(f"Process {p.pid} did not complete execution (state={p.state})")

        tt = p.completion_time - p.arrival_time
        rt = p.first_start_time - p.arrival_time
        wt = p.total_ready_wait

        turnarounds.append(tt)
        responses.append(rt)
        waitings.append(wt)
        total_cpu_busy += p.total_cpu_time

        per_process.append(
            ProcessMetricSummary(
                pid=p.pid,
                arrival_time=p.arrival_time,
                first_start_time=p.first_start_time,
                completion_time=p.completion_time,
                total_cpu_time=p.total_cpu_time,
                ready_wait_time=wt,
                blocked_time=p.total_blocked_time,
                response_time=rt,
                turnaround_time=tt,
                dispatch_count=p.dispatch_count,
            )
        )

    cpu_util = (total_cpu_busy / makespan * 100.0) if makespan > 0 else 0.0
    throughput = (len(processes) / makespan) if makespan > 0 else 0.0
    total_idle = max(0, makespan - total_cpu_busy)

    return SimulationMetrics(
        makespan=makespan,
        total_cpu_busy=total_cpu_busy,
        total_idle_time=total_idle,
        cpu_utilisation_pct=cpu_util,
        throughput=throughput,
        context_switches=context_switches,
        avg_turnaround_time=float(np.mean(turnarounds)),
        std_turnaround_time=float(np.std(turnarounds)),
        avg_response_time=float(np.mean(responses)),
        std_response_time=float(np.std(responses)),
        p95_response_time=float(np.percentile(responses, 95)),
        avg_waiting_time=float(np.mean(waitings)),
        std_waiting_time=float(np.std(waitings)),
        max_waiting_time=int(max(waitings)),
        per_process=per_process,
    )
