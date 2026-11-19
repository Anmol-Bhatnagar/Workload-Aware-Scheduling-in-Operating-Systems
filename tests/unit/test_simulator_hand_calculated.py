"""
Hand-calculated textbook fixture tests verifying FCFS, SJF, RR, and Priority.
Based on standard textbook problems (Silberschatz et al., Operating System Concepts).
"""

import pytest
from scheduling_lab.core.models import Process
from scheduling_lab.core.simulator import CPUSimulator
from scheduling_lab.schedulers.fcfs import FCFSScheduler
from scheduling_lab.schedulers.priority import PriorityScheduler
from scheduling_lab.schedulers.round_robin import RoundRobinScheduler
from scheduling_lab.schedulers.sjf import SJFScheduler


def test_hand_calculated_silberschatz_fcfs():
    """
    Classic example:
    P1: burst=24, arrival=0
    P2: burst=3, arrival=0
    P3: burst=3, arrival=0
    Arrival order / tie-breaker: P1, P2, P3
    Expected timeline:
    P1: [0, 24]  -> wait = 0, turnaround = 24
    P2: [24, 27] -> wait = 24, turnaround = 27
    P3: [27, 30] -> wait = 27, turnaround = 30
    Average wait = 17.0
    Average turnaround = 27.0
    """
    workload = [
        Process("P1", arrival_time=0, priority=1, cpu_bursts=[24]),
        Process("P2", arrival_time=0, priority=1, cpu_bursts=[3]),
        Process("P3", arrival_time=0, priority=1, cpu_bursts=[3]),
    ]
    sim = CPUSimulator(scheduler=FCFSScheduler())
    res = sim.run(workload, scenario_id="textbook_fcfs")

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].first_start_time == 0
    assert p_map["P1"].completion_time == 24
    assert p_map["P1"].total_ready_wait == 0
    assert p_map["P1"].turnaround_time == 24

    assert p_map["P2"].first_start_time == 24
    assert p_map["P2"].completion_time == 27
    assert p_map["P2"].total_ready_wait == 24
    assert p_map["P2"].turnaround_time == 27

    assert p_map["P3"].first_start_time == 27
    assert p_map["P3"].completion_time == 30
    assert p_map["P3"].total_ready_wait == 27
    assert p_map["P3"].turnaround_time == 30

    assert pytest.approx(res.metrics.avg_waiting_time, 1e-4) == 17.0
    assert pytest.approx(res.metrics.avg_turnaround_time, 1e-4) == 27.0
    assert res.metrics.makespan == 30
    assert res.metrics.total_cpu_busy == 30
    assert res.metrics.context_switches == 2


def test_hand_calculated_silberschatz_sjf():
    """
    Same workload under non-preemptive SJF:
    Order: P2 (3), P3 (3), P1 (24)
    P2: [0, 3]   -> wait = 0, turnaround = 3
    P3: [3, 6]   -> wait = 3, turnaround = 6
    P1: [6, 30]  -> wait = 6, turnaround = 30
    Average wait = (0 + 3 + 6) / 3 = 3.0
    Average turnaround = (3 + 6 + 30) / 3 = 13.0
    """
    workload = [
        Process("P1", arrival_time=0, priority=1, cpu_bursts=[24]),
        Process("P2", arrival_time=0, priority=1, cpu_bursts=[3]),
        Process("P3", arrival_time=0, priority=1, cpu_bursts=[3]),
    ]
    sim = CPUSimulator(scheduler=SJFScheduler())
    res = sim.run(workload, scenario_id="textbook_sjf")

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P2"].first_start_time == 0
    assert p_map["P2"].completion_time == 3
    assert p_map["P2"].total_ready_wait == 0

    assert p_map["P3"].first_start_time == 3
    assert p_map["P3"].completion_time == 6
    assert p_map["P3"].total_ready_wait == 3

    assert p_map["P1"].first_start_time == 6
    assert p_map["P1"].completion_time == 30
    assert p_map["P1"].total_ready_wait == 6

    assert pytest.approx(res.metrics.avg_waiting_time, 1e-4) == 3.0
    assert pytest.approx(res.metrics.avg_turnaround_time, 1e-4) == 13.0
    assert res.metrics.makespan == 30
    assert res.metrics.context_switches == 2


def test_hand_calculated_silberschatz_rr():
    """
    Same workload under Round Robin with quantum = 4:
    P1: 24, P2: 3, P3: 3
    Timeline:
    [0, 4]: P1 runs (remaining 20). Preempted at 4. Queue: [P2, P3, P1]
    [4, 7]: P2 runs (burst 3). Terminates at 7. Queue: [P3, P1]
    [7, 10]: P3 runs (burst 3). Terminates at 10. Queue: [P1]
    [10, 30]: P1 finishes remaining 20.
    P1: wait = 6 (during [4, 10)), turnaround = 30
    P2: wait = 4 (during [0, 4)), turnaround = 7
    P3: wait = 7 (during [0, 7)), turnaround = 10
    Average wait = (6 + 4 + 7) / 3 = 17 / 3 = 5.6667
    Average turnaround = (30 + 7 + 10) / 3 = 47 / 3 = 15.6667
    """
    workload = [
        Process("P1", arrival_time=0, priority=1, cpu_bursts=[24]),
        Process("P2", arrival_time=0, priority=1, cpu_bursts=[3]),
        Process("P3", arrival_time=0, priority=1, cpu_bursts=[3]),
    ]
    sim = CPUSimulator(scheduler=RoundRobinScheduler(quantum=4))
    res = sim.run(workload, scenario_id="textbook_rr")

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].turnaround_time == 30
    assert p_map["P1"].total_ready_wait == 6

    assert p_map["P2"].turnaround_time == 7
    assert p_map["P2"].total_ready_wait == 4

    assert p_map["P3"].turnaround_time == 10
    assert p_map["P3"].total_ready_wait == 7

    assert pytest.approx(res.metrics.avg_waiting_time, 1e-4) == 17 / 3
    assert pytest.approx(res.metrics.avg_turnaround_time, 1e-4) == 47 / 3
    assert res.metrics.makespan == 30


def test_hand_calculated_priority():
    """
    Priority test (lower integer = higher priority):
    P1: burst=10, priority=3, arrival=0
    P2: burst=1,  priority=1, arrival=0
    P3: burst=2,  priority=2, arrival=0
    Order: P2 (priority 1), P3 (priority 2), P1 (priority 3)
    P2: [0, 1]  -> wait = 0, turnaround = 1
    P3: [1, 3]  -> wait = 1, turnaround = 3
    P1: [3, 13] -> wait = 3, turnaround = 13
    Average wait = (0 + 1 + 3) / 3 = 4 / 3 = 1.3333
    Average turnaround = (1 + 3 + 13) / 3 = 17 / 3 = 5.6667
    """
    workload = [
        Process("P1", arrival_time=0, priority=3, cpu_bursts=[10]),
        Process("P2", arrival_time=0, priority=1, cpu_bursts=[1]),
        Process("P3", arrival_time=0, priority=2, cpu_bursts=[2]),
    ]
    sim = CPUSimulator(scheduler=PriorityScheduler(lower_is_higher=True))
    res = sim.run(workload, scenario_id="textbook_priority")

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P2"].first_start_time == 0
    assert p_map["P2"].completion_time == 1

    assert p_map["P3"].first_start_time == 1
    assert p_map["P3"].completion_time == 3

    assert p_map["P1"].first_start_time == 3
    assert p_map["P1"].completion_time == 13

    assert pytest.approx(res.metrics.avg_waiting_time, 1e-4) == 4 / 3
    assert pytest.approx(res.metrics.avg_turnaround_time, 1e-4) == 17 / 3
    assert res.metrics.makespan == 13
