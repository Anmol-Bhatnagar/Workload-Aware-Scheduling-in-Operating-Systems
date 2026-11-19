"""
Round Robin (RR) preemptive CPU scheduling policy.
"""

from __future__ import annotations

from typing import List, Optional

from scheduling_lab.core.models import Process
from scheduling_lab.schedulers.base import BaseScheduler


class RoundRobinScheduler(BaseScheduler):
    """Round Robin preemptive scheduler with configurable time quantum."""

    def __init__(self, quantum: int = 5, name: Optional[str] = None) -> None:
        if quantum <= 0:
            raise ValueError(f"Time quantum must be a positive integer, got {quantum}")
        self.quantum = quantum
        super().__init__(name=name or f"RR_Q{quantum}")

    @property
    def is_preemptive(self) -> bool:
        return True

    def select_next(self, ready_queue: List[Process], current_time: int) -> Optional[Process]:
        if not ready_queue:
            return None
        # FIFO selection based on ready queue entry timestamp, then arrival time, then PID
        return min(
            ready_queue,
            key=lambda p: (p.ready_entry_time, p.arrival_time, p.pid),
        )

    def should_preempt(
        self,
        running_process: Process,
        current_time: int,
        ticks_in_quantum: int,
        ready_queue: List[Process],
    ) -> bool:
        # Preempt when quantum duration is reached, provided there are other candidate processes waiting
        if ticks_in_quantum >= self.quantum and len(ready_queue) > 0:
            return True
        return False
