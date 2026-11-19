"""
Unit tests for Process and ProcessState models.
"""

import pytest
from scheduling_lab.core.models import Process, ProcessState


def test_process_initialization_valid():
    p = Process(pid="P1", arrival_time=0, priority=1, cpu_bursts=[5, 3], io_bursts=[2])
    assert p.pid == "P1"
    assert p.arrival_time == 0
    assert p.priority == 1
    assert p.state == ProcessState.NEW
    assert p.total_expected_cpu == 8
    assert p.total_expected_io == 2
    assert p.remaining_cpu_in_burst == 5
    assert not p.is_terminated


def test_process_validation_errors():
    with pytest.raises(ValueError, match="arrival_time must be non-negative"):
        Process(pid="P1", arrival_time=-1, priority=1, cpu_bursts=[5])

    with pytest.raises(ValueError, match="cpu_bursts must contain positive integers"):
        Process(pid="P1", arrival_time=0, priority=1, cpu_bursts=[])

    with pytest.raises(ValueError, match="cpu_bursts must contain positive integers"):
        Process(pid="P1", arrival_time=0, priority=1, cpu_bursts=[0])

    with pytest.raises(ValueError, match="cpu_bursts must contain positive integers"):
        Process(pid="P1", arrival_time=0, priority=1, cpu_bursts=[-4])

    with pytest.raises(ValueError, match="io_bursts must contain non-negative integers"):
        Process(pid="P1", arrival_time=0, priority=1, cpu_bursts=[5], io_bursts=[-1])

    with pytest.raises(ValueError, match="cannot have more io_bursts than cpu_bursts"):
        Process(pid="P1", arrival_time=0, priority=1, cpu_bursts=[5], io_bursts=[2, 3])


def test_process_cloning():
    p1 = Process(pid="P1", arrival_time=2, priority=3, cpu_bursts=[4, 4], io_bursts=[5])
    p1.state = ProcessState.RUNNING
    p1.total_cpu_time = 3
    p1.first_start_time = 2

    clone = p1.clone()
    assert clone.pid == "P1"
    assert clone.state == ProcessState.NEW
    assert clone.total_cpu_time == 0
    assert clone.first_start_time is None
    assert clone.cpu_bursts == [4, 4]
    assert clone.io_bursts == [5]
