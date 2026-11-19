"""
First-Come First-Served (FCFS) CPU scheduling policy.
"""

from __future__ import annotations

from typing import List, Optional

from scheduling_lab.core.models import Process
from scheduling_lab.schedulers.base import BaseScheduler


class FCFSScheduler(BaseScheduler):
    """First-Come, First-Served non-preemptive scheduler."""

    def __init__(self, name: str = "FCFS") -> None:
        super().__init__(name=name)

    def select_next(self, ready_queue: List[Process], current_time: int) -> Optional[Process]:
        if not ready_queue:
            return None
        # Deterministic sorting: ready_entry_time, arrival_time, then pid
        return min(
            ready_queue,
            key=lambda p: (p.ready_entry_time, p.arrival_time, p.pid),
        )
