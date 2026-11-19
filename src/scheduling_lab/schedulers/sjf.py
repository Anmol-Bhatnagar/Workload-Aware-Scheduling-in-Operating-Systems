"""
Shortest Job First (SJF) non-preemptive CPU scheduling policy.
Clairvoyant / offline textbook baseline using known generated burst lengths.
"""

from __future__ import annotations

from typing import List, Optional

from scheduling_lab.core.models import Process
from scheduling_lab.schedulers.base import BaseScheduler


class SJFScheduler(BaseScheduler):
    """
    Shortest Job First non-preemptive scheduler.
    Note: Clairvoyant textbook baseline that selects based on known remaining CPU burst.
    """

    def __init__(self, name: str = "SJF") -> None:
        super().__init__(name=name)

    def select_next(self, ready_queue: List[Process], current_time: int) -> Optional[Process]:
        if not ready_queue:
            return None
        # Deterministic sorting: burst length, ready entry, arrival time, pid
        return min(
            ready_queue,
            key=lambda p: (p.remaining_cpu_in_burst, p.ready_entry_time, p.arrival_time, p.pid),
        )
