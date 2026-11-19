"""
Non-preemptive Priority CPU scheduling policy.
"""

from __future__ import annotations

from typing import List, Optional

from scheduling_lab.core.models import Process
from scheduling_lab.schedulers.base import BaseScheduler


class PriorityScheduler(BaseScheduler):
    """
    Non-preemptive priority scheduler.
    By default, lower numerical value signifies higher scheduling priority (POSIX/UNIX convention).
    """

    def __init__(self, lower_is_higher: bool = True, name: str = "PRIORITY") -> None:
        self.lower_is_higher = lower_is_higher
        super().__init__(name=name)

    def select_next(self, ready_queue: List[Process], current_time: int) -> Optional[Process]:
        if not ready_queue:
            return None

        if self.lower_is_higher:
            return min(
                ready_queue,
                key=lambda p: (p.priority, p.ready_entry_time, p.arrival_time, p.pid),
            )
        else:
            return max(
                ready_queue,
                key=lambda p: (p.priority, -p.ready_entry_time, -p.arrival_time, p.pid),
            )
