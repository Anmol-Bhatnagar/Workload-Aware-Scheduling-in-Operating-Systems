# Literature & Technical Background Review

## 1. Classical CPU Scheduling & Recent Adaptive Approaches

CPU scheduling is a fundamental operating systems mechanism responsible for arbitrating processor access among concurrent threads and processes in the `READY` state. Standard textbook taxonomy partitions scheduling algorithms into non-preemptive strategies (First-Come First-Served [FCFS], Shortest Job First [SJF], Non-preemptive Priority) and preemptive policies (Round Robin [RR], Shortest Remaining Time First [SRTF], Multilevel Feedback Queues [MLFQ]).

While SJF provably minimizes average waiting time for static batch workloads, it represents a clairvoyant baseline requiring advance knowledge of future CPU burst lengths. Round Robin mitigates starvation and achieves low response times for interactive systems by multiplexing CPU time slices (quanta). However, static quantum selection involves an inescapable trade-off: small quanta minimize response latency but amplify context-switching overhead, whereas large quanta degenerate toward FCFS behavior and exacerbate the convoy effect.

Recent research has explored dynamic and adaptive scheduling mechanisms. In particular, the **Agent-Based Adaptive Dynamic Round Robin Scheduling Algorithm (AADRR)** (*IEEE Access*, 2025; DOI: 10.1109/ACCESS.2025.3534031) proposes adjusting quantum boundaries dynamically based on queue statistics. Our investigation takes inspiration from the principle of workload-awareness: rather than attempting runtime agent loops inside kernel dispatch paths, we formulate policy selection as an explainable, pre-execution classification problem using workload-level statistical properties.

## 2. Evolution of Linux CPU Scheduling: From CFS to EEVDF

Textbook discussions often cite the Completely Fair Scheduler (CFS), introduced in Linux 2.6.23, which tracks process virtual runtime (`vruntime`) using a red-black tree. However, beginning in Linux 6.6, modern Linux has transitioned to the **Earliest Eligible Virtual Deadline First (EEVDF)** scheduler, designed by Peter Zijlstra based on Peter Hoon's 1995 framework (Linux Kernel Documentation: `sched-eevdf.html`).

EEVDF separates the concept of *eligibility* (whether a task has consumed less than its fair share of CPU time) from *lag* and *virtual deadline* (the expected time by which an eligible task should complete a slice). This allows Linux to achieve low latency for interactive wakeups without heuristic latency-sensitive tweaks that previously complicated CFS. Our study explicitly references EEVDF as modern OS context, but avoids simulating its intricate kernel mechanics, focusing instead on transparent classical algorithms.

## 3. Storage Block I/O Schedulers in Linux

Storage I/O scheduling operates at the block layer, managing queues of disk requests to optimize device throughput, prevent starvation, and minimize completion latency. Modern Linux kernels employ the multi-queue block layer (`blk-mq`) and expose schedulers via sysfs at `/sys/block/<device>/queue/scheduler` (Linux Kernel Documentation: `switching-sched.html`):
- `none`: Schedulers are bypassed; requests are dispatched directly to hardware queues. This is typically optimal for ultra-fast NVMe solid-state drives with hardware multi-queue parallelism.
- `mq-deadline`: Schedulers sort requests by physical block address for throughput while imposing strict read/write expiration deadlines (typically 500ms for writes, 120ms for reads) to prevent starvation.
- `bfq` (Budget Fair Queueing): Provides proportional bandwidth allocation and low latency for interactive desktop applications by allocating per-process sector budgets.
- `kyber`: A lightweight, latency-oriented scheduler that throttles queue depth when request latency exceeds target thresholds.

In **"Towards Machine Learning-Based I/O Scheduling"** (Stony Brook University, Technical Report FSL-25-07, 2025), Zadok et al. investigate learning-driven storage scheduler selection based on workload characteristics. Our empirical storage add-on aligns with this principle by benchmarking sequential versus random workloads using `fio` (Flexible I/O Tester; Axboe, 2024), measuring the empirical performance spread across exposed schedulers under safe file-backed conditions.
