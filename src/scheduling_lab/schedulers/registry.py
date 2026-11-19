"""
Scheduler registry factory.
"""

from __future__ import annotations

from typing import Any, Dict

from scheduling_lab.schedulers.base import BaseScheduler
from scheduling_lab.schedulers.fcfs import FCFSScheduler
from scheduling_lab.schedulers.priority import PriorityScheduler
from scheduling_lab.schedulers.round_robin import RoundRobinScheduler
from scheduling_lab.schedulers.sjf import SJFScheduler


def create_scheduler(policy_type: str, **kwargs: Any) -> BaseScheduler:
    """Instantiate a scheduler by its type identifier."""
    norm_type = policy_type.lower().strip()
    if norm_type in ("fcfs", "fifo"):
        return FCFSScheduler(name=kwargs.get("name", "FCFS"))
    elif norm_type == "sjf":
        return SJFScheduler(name=kwargs.get("name", "SJF"))
    elif norm_type in ("rr", "round_robin"):
        quantum = kwargs.get("quantum", 5)
        name = kwargs.get("name", f"RR_Q{quantum}")
        return RoundRobinScheduler(quantum=quantum, name=name)
    elif norm_type == "priority":
        lower_is_higher = kwargs.get("lower_is_higher", True)
        name = kwargs.get("name", "PRIORITY")
        return PriorityScheduler(lower_is_higher=lower_is_higher, name=name)
    else:
        raise ValueError(f"Unknown scheduler policy type: '{policy_type}'")
