# Data Dictionary

This document details every schema, feature, event field, and performance metric used across the CPU and I/O experiments.

---

## 1. Process Attributes (`Process` model)

| Field Name | Type | Description |
|---|---|---|
| `pid` | String | Unique process identifier (e.g., `P1`, `P2`) |
| `arrival_time` | Integer | Simulation tick at which process is admitted to the system ($\ge 0$) |
| `priority` | Integer | Scheduling priority level (1 to 5; lower value = higher priority) |
| `cpu_bursts` | List[Integer] | Sequence of CPU execution burst durations (positive integers) |
| `io_bursts` | List[Integer] | Sequence of I/O wait durations between successive CPU bursts ($\ge 0$) |
| `state` | String Enum | Current state: `NEW`, `READY`, `RUNNING`, `BLOCKED`, `TERMINATED` |
| `first_start_time` | Integer / Null | Simulation tick when process is first dispatched to CPU |
| `completion_time` | Integer / Null | Simulation tick when process finishes its final CPU burst |
| `total_cpu_time` | Integer | Accumulated CPU execution ticks |
| `total_ready_wait` | Integer | Accumulated ticks spent waiting in the `READY` queue |
| `total_blocked_time`| Integer | Accumulated ticks spent waiting in `BLOCKED` I/O state |
| `dispatch_count` | Integer | Number of distinct times process was dispatched to CPU |

---

## 2. Pre-Execution Workload Features (`PreExecutionFeatureExtractor`)

These 12 features are computed strictly prior to execution and passed to the machine learning policy recommender.

| Feature Name | Type | Formula / Definition | Leakage Guard |
|---|---|---|---|
| `process_count` | Float | Number of processes in scenario | Safe: set at scenario creation |
| `mean_initial_burst` | Float | Mean duration of first CPU burst $\frac{1}{N}\sum b_{i,0}$ | Safe: known from generated burst table |
| `std_initial_burst` | Float | Standard deviation of first CPU bursts | Safe: known from generated burst table |
| `burst_cv` | Float | Coefficient of variation across all CPU bursts ($\sigma / \mu$) | Safe: known from generated burst table |
| `mean_io_wait` | Float | Mean duration of all I/O waiting intervals | Safe: known from generated burst table |
| `multi_burst_ratio` | Float | Fraction of processes with $> 1$ CPU burst | Safe: known from process structure |
| `cpu_to_io_ratio` | Float | Total expected CPU ticks / (Total expected I/O ticks + 1) | Safe: calculated from burst tables |
| `mean_arrival_gap` | Float | Mean time interval between consecutive arrivals | Safe: derived from arrival schedule |
| `std_arrival_gap` | Float | Standard deviation of arrival gaps | Safe: derived from arrival schedule |
| `short_burst_ratio` | Float | Fraction of CPU bursts with length $\le 3$ ticks | Safe: derived from burst tables |
| `priority_std` | Float | Standard deviation of priority levels | Safe: derived from priority assignments |
| `arrival_burstiness`| Float | Max arrivals in any 5-tick window divided by total processes | Safe: derived from arrival schedule |

*Leakage Prevention Rule:* Neither turnaround time, waiting time, response time, nor context switches may ever be exposed to the feature extractor.

---

## 3. Event Record Fields (`EventRecord`)

Every simulation writes an immutable append-only JSONL log containing:

| Field Name | Type | Description |
|---|---|---|
| `event_id` | Integer | Monotonically increasing event sequence counter |
| `sim_time` | Integer | Simulation tick timestamp |
| `event_type` | String | Event type: `ARRIVAL`, `DISPATCH`, `PREEMPT`, `BURST_COMPLETE`, `IO_BLOCK`, `IO_WAKE`, `TERMINATION`, `IDLE` |
| `pid` | String / Null | Process ID associated with event |
| `state_before` | String / Null | Process state prior to event |
| `state_after` | String / Null | Process state following event |
| `cpu_pid_before` | String / Null | PID executing on CPU before step |
| `cpu_pid_after` | String / Null | PID executing on CPU after step |
| `ready_queue` | List[String] | PIDs currently waiting in ready queue in arrival order |
| `blocked_processes`| List[String] | PIDs currently in blocked I/O state |
| `policy` | String | Active scheduler policy identifier |
| `decision_reason` | String | Human-readable explanation of scheduler event |

---

## 4. Performance Metrics (`SimulationMetrics`)

| Metric | Unit | Mathematical Definition |
|---|---|---|
| `makespan` | Ticks | Total simulation duration from $t=0$ until all processes terminate |
| `total_cpu_busy` | Ticks | Sum of ticks during which CPU executed any process |
| `total_idle_time` | Ticks | Sum of ticks during which CPU had no ready process to execute |
| `cpu_utilisation_pct` | % | $(\text{total\_cpu\_busy} / \text{makespan}) \times 100$ |
| `throughput` | Proc/tick | $\text{completed processes} / \text{makespan}$ |
| `context_switches`| Count | Number of CPU switches between distinct non-idle processes |
| `avg_turnaround_time`| Ticks | Mean of $(T_{completion} - T_{arrival})$ across processes |
| `avg_response_time` | Ticks | Mean of $(T_{first\_start} - T_{arrival})$ across processes |
| `p95_response_time` | Ticks | 95th percentile of per-process response times |
| `avg_waiting_time` | Ticks | Mean of total time spent in `READY` queue across processes |
| `max_waiting_time` | Ticks | Maximum ready queue wait experienced by any single process |
