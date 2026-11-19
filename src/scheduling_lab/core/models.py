"""
Core data models for processes, simulation events, timeline intervals, and metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProcessState(str, Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"


class EventType(str, Enum):
    ARRIVAL = "ARRIVAL"
    DISPATCH = "DISPATCH"
    PREEMPT = "PREEMPT"
    BURST_COMPLETE = "BURST_COMPLETE"
    IO_BLOCK = "IO_BLOCK"
    IO_WAKE = "IO_WAKE"
    TERMINATION = "TERMINATION"
    IDLE = "IDLE"


@dataclass
class Process:
    pid: str
    arrival_time: int
    priority: int
    cpu_bursts: List[int]
    io_bursts: List[int] = field(default_factory=list)

    # Runtime state tracking
    state: ProcessState = ProcessState.NEW
    current_burst_index: int = 0
    remaining_cpu_in_burst: int = 0
    remaining_io_in_burst: int = 0
    ready_entry_time: int = 0

    # Lifecycle metric timestamps
    first_start_time: Optional[int] = None
    completion_time: Optional[int] = None
    total_cpu_time: int = 0
    total_ready_wait: int = 0
    total_blocked_time: int = 0
    dispatch_count: int = 0

    def __post_init__(self) -> None:
        if self.arrival_time < 0:
            raise ValueError(f"Process {self.pid}: arrival_time must be non-negative, got {self.arrival_time}")
        if not self.cpu_bursts or any(b <= 0 for b in self.cpu_bursts):
            raise ValueError(f"Process {self.pid}: cpu_bursts must contain positive integers, got {self.cpu_bursts}")
        if any(b < 0 for b in self.io_bursts):
            raise ValueError(f"Process {self.pid}: io_bursts must contain non-negative integers, got {self.io_bursts}")
        if len(self.io_bursts) > len(self.cpu_bursts):
            raise ValueError(f"Process {self.pid}: cannot have more io_bursts than cpu_bursts")

        self.remaining_cpu_in_burst = self.cpu_bursts[0]
        self.ready_entry_time = self.arrival_time

    @property
    def total_expected_cpu(self) -> int:
        return sum(self.cpu_bursts)

    @property
    def total_expected_io(self) -> int:
        return sum(self.io_bursts)

    @property
    def is_terminated(self) -> bool:
        return self.state == ProcessState.TERMINATED

    @property
    def turnaround_time(self) -> Optional[int]:
        if self.completion_time is None:
            return None
        return self.completion_time - self.arrival_time

    @property
    def response_time(self) -> Optional[int]:
        if self.first_start_time is None:
            return None
        return self.first_start_time - self.arrival_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "priority": self.priority,
            "cpu_bursts": list(self.cpu_bursts),
            "io_bursts": list(self.io_bursts),
            "state": self.state.value,
            "first_start_time": self.first_start_time,
            "completion_time": self.completion_time,
            "total_cpu_time": self.total_cpu_time,
            "total_ready_wait": self.total_ready_wait,
            "total_blocked_time": self.total_blocked_time,
            "dispatch_count": self.dispatch_count,
            "turnaround_time": self.turnaround_time,
            "response_time": self.response_time,
        }

    def clone(self) -> "Process":
        """Return a fresh un-executed copy with identical initial parameters."""
        return Process(
            pid=self.pid,
            arrival_time=self.arrival_time,
            priority=self.priority,
            cpu_bursts=list(self.cpu_bursts),
            io_bursts=list(self.io_bursts),
        )


@dataclass
class TimelineInterval:
    pid: str  # PID or "IDLE"
    start_time: int
    end_time: int
    interval_type: str  # "CPU", "IO", "IDLE"

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time


@dataclass
class EventRecord:
    event_id: int
    sim_time: int
    event_type: str
    pid: Optional[str]
    state_before: Optional[str]
    state_after: Optional[str]
    cpu_pid_before: Optional[str]
    cpu_pid_after: Optional[str]
    ready_queue: List[str]
    blocked_processes: List[str]
    policy: str
    decision_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "sim_time": self.sim_time,
            "event_type": self.event_type,
            "pid": self.pid,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "cpu_pid_before": self.cpu_pid_before,
            "cpu_pid_after": self.cpu_pid_after,
            "ready_queue": list(self.ready_queue),
            "blocked_processes": list(self.blocked_processes),
            "policy": self.policy,
            "decision_reason": self.decision_reason,
        }
