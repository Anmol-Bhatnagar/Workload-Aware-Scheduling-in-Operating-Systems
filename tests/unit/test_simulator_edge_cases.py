"""
Unit tests for edge cases, I/O blocking, CPU idle periods, conservation laws, and determinism.
"""

import pytest
from scheduling_lab.core.models import Process
from scheduling_lab.core.simulator import CPUSimulator
from scheduling_lab.schedulers.fcfs import FCFSScheduler
from scheduling_lab.schedulers.round_robin import RoundRobinScheduler
from scheduling_lab.schedulers.sjf import SJFScheduler


def test_cpu_idle_gap():
    """
    P1 arrives at 0, burst 3. Completes at 3.
    P2 arrives at 8, burst 4.
    Simulator must record idle interval [3, 8).
    Total makespan = 12.
    CPU busy = 7. Idle = 5.
    """
    workload = [
        Process("P1", arrival_time=0, priority=1, cpu_bursts=[3]),
        Process("P2", arrival_time=8, priority=1, cpu_bursts=[4]),
    ]
    sim = CPUSimulator(scheduler=FCFSScheduler())
    res = sim.run(workload, scenario_id="idle_gap")

    assert res.metrics.makespan == 12
    assert res.metrics.total_cpu_busy == 7
    assert res.metrics.total_idle_time == 5
    assert pytest.approx(res.metrics.cpu_utilisation_pct, 1e-2) == (7 / 12 * 100)

    idle_intervals = [i for i in res.timeline if i.interval_type == "IDLE"]
    assert len(idle_intervals) == 1
    assert idle_intervals[0].start_time == 3
    assert idle_intervals[0].end_time == 8


def test_multiburst_io_blocking():
    """
    P1: CPU(2) -> IO(3) -> CPU(2). Arrival 0.
    P2: CPU(2) -> IO(1) -> CPU(1). Arrival 1.
    Timeline trace:
    t=0: P1 runs [0, 2). At 2, P1 blocks in IO for 3 ticks (wakes at t=5).
    t=1: P2 arrived, queued.
    t=2: P2 dispatched. Runs CPU [2, 4). At 4, P2 blocks in IO for 1 tick (wakes at t=5).
    t=4: Both in IO. Idle [4, 5).
    t=5: Both wake up! P1 and P2 enter ready queue.
         Deterministic tie-breaker: P1 arrived earlier (0 vs 1).
         P1 runs [5, 7). Terminates at 7.
    t=7: P2 runs [7, 8). Terminates at 8.
    """
    p1 = Process("P1", arrival_time=0, priority=1, cpu_bursts=[2, 2], io_bursts=[3])
    p2 = Process("P2", arrival_time=1, priority=1, cpu_bursts=[2, 1], io_bursts=[1])

    sim = CPUSimulator(scheduler=FCFSScheduler())
    res = sim.run([p1, p2], scenario_id="io_multiburst")

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].total_cpu_time == 4
    assert p_map["P1"].total_blocked_time == 3
    assert p_map["P1"].completion_time == 7
    assert p_map["P1"].turnaround_time == 7

    assert p_map["P2"].total_cpu_time == 3
    assert p_map["P2"].total_blocked_time == 1
    assert p_map["P2"].completion_time == 8
    assert p_map["P2"].turnaround_time == 7

    assert res.metrics.makespan == 8
    assert res.metrics.total_cpu_busy == 7
    assert res.metrics.total_idle_time == 1


def test_rr_huge_quantum_equals_fcfs():
    """Round Robin with quantum larger than all bursts should produce identical output to FCFS."""
    workload = [
        Process("P1", arrival_time=0, priority=1, cpu_bursts=[4, 3], io_bursts=[2]),
        Process("P2", arrival_time=1, priority=1, cpu_bursts=[5, 2], io_bursts=[3]),
        Process("P3", arrival_time=3, priority=1, cpu_bursts=[6]),
    ]
    sim_fcfs = CPUSimulator(scheduler=FCFSScheduler())
    sim_rr = CPUSimulator(scheduler=RoundRobinScheduler(quantum=1000))

    res_fcfs = sim_fcfs.run(workload)
    res_rr = sim_rr.run(workload)

    assert res_fcfs.metrics.makespan == res_rr.metrics.makespan
    assert res_fcfs.metrics.avg_waiting_time == res_rr.metrics.avg_waiting_time
    assert res_fcfs.metrics.avg_turnaround_time == res_rr.metrics.avg_turnaround_time
    assert res_fcfs.metrics.context_switches == res_rr.metrics.context_switches


def test_simulation_determinism():
    """Running the exact same workload twice must yield identical traces and metrics."""
    workload = [
        Process("P1", arrival_time=0, priority=2, cpu_bursts=[3, 4], io_bursts=[2]),
        Process("P2", arrival_time=2, priority=1, cpu_bursts=[5, 1], io_bursts=[1]),
        Process("P3", arrival_time=4, priority=3, cpu_bursts=[2]),
    ]
    sim = CPUSimulator(scheduler=RoundRobinScheduler(quantum=2))

    res1 = sim.run(workload, scenario_id="det_check", seed=42)
    res2 = sim.run(workload, scenario_id="det_check", seed=42)

    assert res1.metrics.to_dict() == res2.metrics.to_dict()
    assert len(res1.events) == len(res2.events)
    for e1, e2 in zip(res1.events, res2.events):
        assert e1.to_dict() == e2.to_dict()
