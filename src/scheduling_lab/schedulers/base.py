"""
Abstract base class and registry for CPU scheduling policies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from scheduling_lab.core.models import Process


class BaseScheduler(ABC):
    """Abstract CPU scheduler strategy."""

    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def is_preemptive(self) -> bool:
        """Whether this scheduler policy supports preemption."""
        return False

    @abstractmethod
    def select_next(self, ready_queue: List[Process], current_time: int) -> Optional[Process]:
        """
        Select the next process to execute from the ready queue.
        Must not mutate the ready queue directly; the simulator manages queue membership.
        """
        pass

    def should_preempt(
        self,
        running_process: Process,
        current_time: int,
        ticks_in_quantum: int,
        ready_queue: List[Process],
    ) -> bool:
        """
        Determine if the currently running process should be preempted at current_time.
        Defaults to False for non-preemptive schedulers.
        """
        return False

    def on_admit(self, process: Process, current_time: int) -> None:
        """Callback when a process is admitted or readmitted to the ready queue."""
        pass

    def on_dispatch(self, process: Process, current_time: int) -> None:
        """Callback when a process is dispatched to the CPU."""
        pass

    def on_preempt(self, process: Process, current_time: int) -> None:
        """Callback when a process is preempted."""
        pass

    def on_terminate(self, process: Process, current_time: int) -> None:
        """Callback when a process terminates."""
        pass
