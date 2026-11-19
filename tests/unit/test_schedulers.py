"""
Unit tests for scheduler selection logic and priority ordering.
"""

from scheduling_lab.core.models import Process
from scheduling_lab.schedulers.fcfs import FCFSScheduler
from scheduling_lab.schedulers.priority import PriorityScheduler
from scheduling_lab.schedulers.round_robin import RoundRobinScheduler
from scheduling_lab.schedulers.sjf import SJFScheduler
from scheduling_lab.schedulers.registry import create_scheduler


def test_fcfs_selection():
    fcfs = FCFSScheduler()
    p1 = Process("P1", arrival_time=0, priority=1, cpu_bursts=[5])
    p2 = Process("P2", arrival_time=0, priority=1, cpu_bursts=[2])
    p1.ready_entry_time = 0
    p2.ready_entry_time = 1

    selected = fcfs.select_next([p2, p1], current_time=2)
    assert selected is not None
    assert selected.pid == "P1"


def test_sjf_selection_shortest_burst():
    sjf = SJFScheduler()
    p1 = Process("P1", arrival_time=0, priority=1, cpu_bursts=[10])
    p2 = Process("P2", arrival_time=0, priority=1, cpu_bursts=[3])
    p3 = Process("P3", arrival_time=0, priority=1, cpu_bursts=[7])

    selected = sjf.select_next([p1, p2, p3], current_time=0)
    assert selected is not None
    assert selected.pid == "P2"


def test_priority_selection_lower_is_higher():
    pri = PriorityScheduler(lower_is_higher=True)
    p1 = Process("P1", arrival_time=0, priority=5, cpu_bursts=[4])
    p2 = Process("P2", arrival_time=0, priority=1, cpu_bursts=[4])
    p3 = Process("P3", arrival_time=0, priority=3, cpu_bursts=[4])

    selected = pri.select_next([p1, p2, p3], current_time=0)
    assert selected is not None
    assert selected.pid == "P2"


def test_round_robin_preemption_trigger():
    rr = RoundRobinScheduler(quantum=3)
    p1 = Process("P1", arrival_time=0, priority=1, cpu_bursts=[10])
    p2 = Process("P2", arrival_time=0, priority=1, cpu_bursts=[5])

    # No preemption before quantum
    assert not rr.should_preempt(p1, current_time=2, ticks_in_quantum=2, ready_queue=[p2])
    # Preemption triggers at quantum with waiting processes
    assert rr.should_preempt(p1, current_time=3, ticks_in_quantum=3, ready_queue=[p2])
    # No preemption if ready_queue is empty
    assert not rr.should_preempt(p1, current_time=3, ticks_in_quantum=3, ready_queue=[])


def test_scheduler_registry_creation():
    s1 = create_scheduler("fcfs")
    assert isinstance(s1, FCFSScheduler)
    s2 = create_scheduler("sjf")
    assert isinstance(s2, SJFScheduler)
    s3 = create_scheduler("rr", quantum=4)
    assert isinstance(s3, RoundRobinScheduler)
    assert s3.quantum == 4
    s4 = create_scheduler("priority")
    assert isinstance(s4, PriorityScheduler)
