"""
Discrete-Event CPU Scheduling Simulation Engine.
Implements single-CPU deterministic tick-based simulation with verified event ordering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from scheduling_lab.core.models import (
    EventRecord,
    EventType,
    Process,
    ProcessState,
    TimelineInterval,
)
from scheduling_lab.core.metrics import SimulationMetrics, calculate_metrics
from scheduling_lab.core.validation import validate_simulation_correctness
from scheduling_lab.schedulers.base import BaseScheduler


@dataclass
class SimulationResult:
    scheduler_name: str
    scenario_id: str
    seed: Optional[int]
    processes: List[Process]
    metrics: SimulationMetrics
    timeline: List[TimelineInterval]
    events: List[EventRecord]
    raw_tick_log: List[Tuple[int, str]] = field(default_factory=list)


class CPUSimulator:
    """
    Deterministic single-CPU discrete-event simulation engine.
    Follows fixed tick progression and event resolution order.
    """

    def __init__(
        self,
        scheduler: BaseScheduler,
        context_switch_cost: int = 0,
        max_ticks: int = 100_000,
    ) -> None:
        self.scheduler = scheduler
        self.context_switch_cost = context_switch_cost
        self.max_ticks = max_ticks

    def run(
        self,
        process_workload: List[Process],
        scenario_id: str = "custom",
        seed: Optional[int] = None,
        validate: bool = True,
    ) -> SimulationResult:
        """Execute simulation to completion on a cloned set of processes."""
        if not process_workload:
            raise ValueError("Cannot run simulation with an empty process list")

        # Clone processes to avoid modifying caller inputs
        processes: List[Process] = [p.clone() for p in process_workload]
        processes_by_pid: Dict[str, Process] = {p.pid: p for p in processes}

        ready_queue: List[Process] = []
        blocked_list: List[Process] = []
        unadmitted: List[Process] = sorted(
            [p for p in processes],
            key=lambda p: (p.arrival_time, p.pid),
        )

        running_process: Optional[Process] = None
        ticks_in_quantum: int = 0
        last_running_pid: Optional[str] = None
        context_switch_count: int = 0

        current_time: int = 0
        events: List[EventRecord] = []
        event_counter: int = 0

        raw_cpu_ticks: List[Tuple[int, str]] = []

        def log_event(
            event_type: EventType,
            pid: Optional[str],
            state_before: Optional[str],
            state_after: Optional[str],
            cpu_before: Optional[str],
            cpu_after: Optional[str],
            reason: str,
        ) -> None:
            nonlocal event_counter
            event_counter += 1
            events.append(
                EventRecord(
                    event_id=event_counter,
                    sim_time=current_time,
                    event_type=event_type.value,
                    pid=pid,
                    state_before=state_before,
                    state_after=state_after,
                    cpu_pid_before=cpu_before,
                    cpu_pid_after=cpu_after,
                    ready_queue=[p.pid for p in ready_queue],
                    blocked_processes=[p.pid for p in blocked_list],
                    policy=self.scheduler.name,
                    decision_reason=reason,
                )
            )

        while True:
            # Check for overall completion
            all_terminated = all(p.is_terminated for p in processes)
            if all_terminated:
                break

            if current_time >= self.max_ticks:
                raise RuntimeError(
                    f"Simulation exceeded max_ticks safety limit ({self.max_ticks}). "
                    f"Possible livelock or deadlock detected."
                )

            # Check if any progress is possible
            no_ready = len(ready_queue) == 0
            no_running = running_process is None
            no_blocked = len(blocked_list) == 0
            no_arrivals = len(unadmitted) == 0
            if no_ready and no_running and no_blocked and no_arrivals:
                raise RuntimeError("Deadlock: unfinished processes exist but no future events can occur.")

            cpu_before_step = running_process.pid if running_process else None

            # --- Step 1: Complete CPU burst ending at this timestamp ---
            if running_process is not None:
                if running_process.remaining_cpu_in_burst == 0:
                    running_process.current_burst_index += 1
                    # Check if process has more bursts or terminates
                    if running_process.current_burst_index < len(running_process.cpu_bursts):
                        io_wait = running_process.io_bursts[running_process.current_burst_index - 1]
                        if io_wait > 0:
                            running_process.state = ProcessState.BLOCKED
                            running_process.remaining_io_in_burst = io_wait
                            blocked_list.append(running_process)
                            log_event(
                                EventType.IO_BLOCK,
                                running_process.pid,
                                ProcessState.RUNNING.value,
                                ProcessState.BLOCKED.value,
                                cpu_before_step,
                                None,
                                f"CPU burst completed; entering I/O wait for {io_wait} ticks",
                            )
                        else:
                            # 0-length IO wait: re-enters ready queue immediately
                            running_process.state = ProcessState.READY
                            running_process.ready_entry_time = current_time
                            running_process.remaining_cpu_in_burst = running_process.cpu_bursts[
                                running_process.current_burst_index
                            ]
                            ready_queue.append(running_process)
                            log_event(
                                EventType.BURST_COMPLETE,
                                running_process.pid,
                                ProcessState.RUNNING.value,
                                ProcessState.READY.value,
                                cpu_before_step,
                                None,
                                "CPU burst completed; 0 I/O wait, re-entering ready queue",
                            )
                    else:
                        running_process.state = ProcessState.TERMINATED
                        running_process.completion_time = current_time
                        self.scheduler.on_terminate(running_process, current_time)
                        log_event(
                            EventType.TERMINATION,
                            running_process.pid,
                            ProcessState.RUNNING.value,
                            ProcessState.TERMINATED.value,
                            cpu_before_step,
                            None,
                            "Final CPU burst completed; process terminated",
                        )
                        if all(p.is_terminated for p in processes):
                            running_process = None
                            break

                    running_process = None
                    ticks_in_quantum = 0

            # --- Step 2: Move processes whose simulated I/O wait ends now from BLOCKED to READY ---
            woken_processes: List[Process] = []
            remaining_blocked: List[Process] = []
            for p in blocked_list:
                if p.remaining_io_in_burst == 0:
                    woken_processes.append(p)
                else:
                    remaining_blocked.append(p)

            blocked_list = remaining_blocked
            # Deterministic ordering for simultaneous unblocks: pid
            woken_processes.sort(key=lambda p: p.pid)
            for p in woken_processes:
                p.state = ProcessState.READY
                p.ready_entry_time = current_time
                p.remaining_cpu_in_burst = p.cpu_bursts[p.current_burst_index]
                ready_queue.append(p)
                self.scheduler.on_admit(p, current_time)
                log_event(
                    EventType.IO_WAKE,
                    p.pid,
                    ProcessState.BLOCKED.value,
                    ProcessState.READY.value,
                    running_process.pid if running_process else None,
                    running_process.pid if running_process else None,
                    "I/O wait finished; entering ready queue",
                )

            # --- Step 3: Admit newly arrived processes ---
            newly_arrived: List[Process] = []
            remaining_unadmitted: List[Process] = []
            for p in unadmitted:
                if p.arrival_time == current_time:
                    newly_arrived.append(p)
                else:
                    remaining_unadmitted.append(p)

            unadmitted = remaining_unadmitted
            # Deterministic sorting for simultaneous arrivals: pid
            newly_arrived.sort(key=lambda p: p.pid)
            for p in newly_arrived:
                p.state = ProcessState.READY
                p.ready_entry_time = current_time
                ready_queue.append(p)
                self.scheduler.on_admit(p, current_time)
                log_event(
                    EventType.ARRIVAL,
                    p.pid,
                    ProcessState.NEW.value,
                    ProcessState.READY.value,
                    running_process.pid if running_process else None,
                    running_process.pid if running_process else None,
                    "Process arrived in system",
                )

            # --- Step 4: Apply preemption / quantum-expiry rules ---
            if running_process is not None and self.scheduler.is_preemptive:
                should_preempt = self.scheduler.should_preempt(
                    running_process, current_time, ticks_in_quantum, ready_queue
                )
                if should_preempt:
                    # Preempt process only if there are other candidates waiting or to rotate
                    running_process.state = ProcessState.READY
                    running_process.ready_entry_time = current_time
                    ready_queue.append(running_process)
                    self.scheduler.on_preempt(running_process, current_time)
                    log_event(
                        EventType.PREEMPT,
                        running_process.pid,
                        ProcessState.RUNNING.value,
                        ProcessState.READY.value,
                        running_process.pid,
                        None,
                        f"Quantum expired ({ticks_in_quantum} ticks); preempted to ready queue",
                    )
                    running_process = None
                    ticks_in_quantum = 0
                elif hasattr(self.scheduler, "quantum") and ticks_in_quantum >= getattr(self.scheduler, "quantum"):
                    # Quantum reached but no other candidates waiting; reset quantum for running process
                    ticks_in_quantum = 0

            # --- Step 5: Select a READY process if CPU is idle ---
            if running_process is None and ready_queue:
                next_proc = self.scheduler.select_next(ready_queue, current_time)
                if next_proc is not None:
                    ready_queue.remove(next_proc)
                    running_process = next_proc
                    running_process.state = ProcessState.RUNNING
                    ticks_in_quantum = 0

                    if running_process.first_start_time is None:
                        running_process.first_start_time = current_time

                    running_process.dispatch_count += 1
                    self.scheduler.on_dispatch(running_process, current_time)

                    # Context switch accounting: between distinct non-idle PIDs
                    if last_running_pid is not None and last_running_pid != running_process.pid:
                        context_switch_count += 1

                    last_running_pid = running_process.pid

                    log_event(
                        EventType.DISPATCH,
                        running_process.pid,
                        ProcessState.READY.value,
                        ProcessState.RUNNING.value,
                        None,
                        running_process.pid,
                        f"Dispatched by {self.scheduler.name}",
                    )

            # --- Step 6: Record CPU allocation for interval [current_time, current_time + 1) ---
            if running_process is not None:
                raw_cpu_ticks.append((current_time, running_process.pid))
            else:
                raw_cpu_ticks.append((current_time, "IDLE"))

            # --- Step 7: Advance counters for 1 tick of execution ---
            # 7a. Running process
            if running_process is not None:
                running_process.total_cpu_time += 1
                running_process.remaining_cpu_in_burst -= 1
                ticks_in_quantum += 1

            # 7b. Ready processes
            for p in ready_queue:
                p.total_ready_wait += 1

            # 7c. Blocked processes
            for p in blocked_list:
                p.total_blocked_time += 1
                p.remaining_io_in_burst -= 1

            current_time += 1

        makespan = current_time

        # Build timeline intervals from raw_cpu_ticks
        timeline = self._build_timeline(raw_cpu_ticks)

        # Calculate metrics
        metrics = calculate_metrics(
            processes=processes,
            timeline=timeline,
            context_switches=context_switch_count,
            makespan=makespan,
        )

        if validate:
            validate_simulation_correctness(processes, metrics)

        return SimulationResult(
            scheduler_name=self.scheduler.name,
            scenario_id=scenario_id,
            seed=seed,
            processes=processes,
            metrics=metrics,
            timeline=timeline,
            events=events,
            raw_tick_log=raw_cpu_ticks,
        )

    def _build_timeline(self, raw_ticks: List[Tuple[int, str]]) -> List[TimelineInterval]:
        """Compress consecutive single-tick CPU allocations into TimelineIntervals."""
        if not raw_ticks:
            return []

        intervals: List[TimelineInterval] = []
        curr_pid = raw_ticks[0][1]
        start_tick = raw_ticks[0][0]

        for tick, pid in raw_ticks[1:]:
            if pid != curr_pid:
                intervals.append(
                    TimelineInterval(
                        pid=curr_pid,
                        start_time=start_tick,
                        end_time=tick,
                        interval_type="IDLE" if curr_pid == "IDLE" else "CPU",
                    )
                )
                curr_pid = pid
                start_tick = tick

        # Append last interval
        final_tick = raw_ticks[-1][0] + 1
        intervals.append(
            TimelineInterval(
                pid=curr_pid,
                start_time=start_tick,
                end_time=final_tick,
                interval_type="IDLE" if curr_pid == "IDLE" else "CPU",
            )
        )

        return intervals
