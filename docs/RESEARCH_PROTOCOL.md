# Research Protocol: Intelligent Workload-Aware Scheduling Lab

**Version:** 1.0.0 (Frozen Protocol)  
**Date:** 2026-11-19  
**Status:** FROZEN — Any deviations must be explicitly recorded in this document as exploratory analysis.

---

## 1. Research Scope and Objectives

The objective of this research is to evaluate whether observable, pre-execution workload characteristics can guide the automated selection of CPU scheduling policies, and to conduct an empirical comparative study of storage I/O schedulers under varying access patterns on Linux.

---

## 2. Research Questions (RQs)

- **RQ1 (CPU Policy Comparison):** How do classical scheduling algorithms (FCFS, Shortest Job First, Round Robin, and Non-preemptive Priority) compare across synthetic workload families (CPU-bound, I/O-bound, interactive, mixed, bursty arrivals) in terms of turnaround time, response time, waiting time, and context-switch frequency?
- **RQ2 (Workload-Aware Policy Recommendation):** Can a lightweight, interpretable Decision Tree classifier trained on pre-execution workload statistical features recommend scheduling policies/configurations that achieve lower composite cost than fixed default policies on unseen held-out workloads?
- **RQ3 (Storage I/O Scheduler Dynamics):** On supported Linux block devices, how do exposed I/O schedulers (e.g. `none`, `mq-deadline`, `bfq`, `kyber`) behave across sequential read, random read, random write, and mixed workloads in terms of throughput (MiB/s), IOPS, and latency percentiles?
- **RQ4 (Overhead & Policy Trade-offs):** What is the recommendation latency overhead of the ML selector relative to simulated workload duration, and under what workload conditions does a classical fixed policy remain superior or equal to the recommender?

---

## 3. Formal Hypotheses

- **H1:** No single classical CPU scheduling policy dominates across all workload families and performance metrics.
- **H2:** A Decision Tree model trained on workload-level features achieves lower average composite cost on held-out test scenarios than at least one fixed-policy baseline (specifically FCFS and fixed RR with q=5).
- **H3:** The workload-aware selector does not win across 100% of individual scenarios; its primary utility lies in risk minimization and reducing average regret across heterogeneous workload mixes.
- **H4:** Linux block I/O scheduler performance rankings vary significantly with workload access patterns (e.g., sequential vs. random). If the test environment exposes only a single scheduler (e.g. `none` in virtualized/cloud disks), this hypothesis cannot be tested, and the environment constraint will be reported as an explicit limitation.
- **H5:** Recommender decision latency is under 1 millisecond per workload scenario, negligible relative to simulated makespan, but tracked as a distinct tool overhead rather than injected into simulated OS execution metrics.

---

## 4. Workload Families and Parameter Distributions

Each scenario contains $N$ processes (default $N=10$, range 5–25) with deterministic arrival times, priority levels, and alternating CPU/IO bursts.

| Workload Family | CPU Burst Characteristic | I/O Wait Characteristic | Arrival Pattern | Core Evaluation Goal |
|---|---|---|---|---|
| **CPU-Bound** | Long bursts (Uniform 15–40) | Infrequent / short (Uniform 0–2) | Poisson / steady arrival | Throughput and batch processing |
| **I/O-Bound** | Short bursts (Uniform 1–4) | Long / frequent waits (Uniform 8–20) | Steady arrival | Ready queue re-entry & waiting time |
| **Interactive** | Very short bursts (Uniform 1–3) | Moderate waits (Uniform 3–8) | Frequent arrivals (gaps 0–2) | Minimizing response time |
| **Mixed** | Bimodal mix of CPU and I/O processes | Varied across process classes | Steady arrival | Resource contention handling |
| **Bursty Arrivals**| Mixed burst lengths | Mixed waits | Batched arrival bursts separated by idle gaps | Queue congestion management |

---

## 5. Candidate Policies and Configurations

1. `FCFS`: First-Come First-Served (non-preemptive).
2. `SJF`: Shortest Job First (non-preemptive, clairvoyant baseline using known next burst length).
3. `PRIORITY`: Non-preemptive priority scheduling (lower numerical priority value = higher priority, with deterministic PID tie-breaking).
4. `RR_Q2`: Round Robin with time quantum $q = 2$.
5. `RR_Q5`: Round Robin with time quantum $q = 5$ (standard reference baseline).
6. `RR_Q10`: Round Robin with time quantum $q = 10$.

---

## 6. Pre-Execution Workload Feature Set

To prevent data leakage, only pre-execution summary features are supplied to the recommender:
1. `process_count`: Total number of processes.
2. `mean_initial_burst`: Mean duration of each process's first CPU burst.
3. `std_initial_burst`: Standard deviation of first CPU bursts.
4. `burst_cv`: Coefficient of variation of CPU bursts ($\sigma / \mu$).
5. `mean_io_wait`: Mean duration of simulated I/O waits.
6. `multi_burst_ratio`: Fraction of processes having $>1$ CPU burst.
7. `cpu_to_io_ratio`: Total expected CPU time divided by total expected I/O wait time.
8. `mean_arrival_gap`: Mean time gap between successive process arrivals.
9. `std_arrival_gap`: Standard deviation of arrival gaps.
10. `short_burst_ratio`: Proportion of bursts $\le 3$ time units.
11. `priority_std`: Standard deviation of assigned priorities.
12. `arrival_burstiness`: Peak arrival density (max arrivals in any 5-unit window / total processes).

*Data Leakage Prohibition:* Turnaround time, response time, waiting time, context switches, or any post-simulation metric must never be passed to the recommender as input features.

---

## 7. Metrics & Objective Function

### 7.1 Component Metric Definitions
- **Turnaround Time ($T_{ta}$):** $T_{completion} - T_{arrival}$
- **Response Time ($T_{resp}$):** $T_{first\_dispatch} - T_{arrival}$
- **Ready Waiting Time ($T_{wait}$):** Total simulated ticks in `READY` queue (excluding `BLOCKED` I/O time).
- **Context Switches ($CS$):** Number of CPU transitions between distinct PIDs (excluding transitions to/from idle).
- **CPU Utilisation ($U$):** $(\sum \text{Busy Ticks} / \text{Total Makespan}) \times 100\%$.

### 7.2 Composite Cost Function
For each scenario $s$ and policy $p$, component metrics are min-max normalized across all candidate policies evaluated on scenario $s$:
$$\hat{M}(s, p) = \frac{M(s, p) - \min_{p'} M(s, p')}{\max_{p'} M(s, p') - \min_{p'} M(s, p') + \epsilon}$$
If $\max M = \min M$, then $\hat{M}(s, p) = 0.5$.

For CPU Utilisation, cost is inverted so lower is better: $\hat{U}_{cost} = 1 - \hat{U}$.

$$\text{Composite Cost}(s, p) = 0.30 \times \hat{T}_{resp} + 0.25 \times \hat{T}_{wait} + 0.20 \times \hat{T}_{ta} + 0.15 \times \hat{CS} + 0.10 \times \hat{U}_{cost}$$

The winning policy label for scenario $s$ is:
$$y(s) = \arg\min_p \text{Composite Cost}(s, p)$$

---

## 8. Experimental Partitioning & Validation Protocol

- **Dataset Size:** 500 scenarios (100 per family) for full study; 25 scenarios (5 per family) for pilot.
- **Data Splitting:** Stratified by workload family, grouped strictly by `scenario_id`:
  - 70% Training (~350 scenarios)
  - 15% Validation (~75 scenarios)
  - 15% Held-Out Test (~75 scenarios)
- **Model Freezing:** Hyperparameters (e.g. tree depth) tuned exclusively on training/validation splits. Once evaluated on the held-out test split, no further model tuning is permitted.

---

## 9. Baseline Comparisons

1. `Always FCFS`: Naive FIFO queueing.
2. `Always RR_Q5`: Standard Round Robin baseline.
3. `Best Fixed Policy`: The single classical policy yielding lowest average composite cost across training/validation data.
4. `Per-Scenario Oracle`: The theoretical upper bound selecting $\arg\min_p \text{Cost}(s, p)$ for each test scenario.

---

## 10. Linux Storage I/O Safety & Protocol

- **Target Safety:** File-backed testing ONLY targeting a temporary file in `data/scratch/fio_test.dat`.
- **Prohibited:** Any raw block-device targeting (`/dev/sda`, `/dev/nvme0n1`, etc.).
- **Workloads:** Sequential Read, Random Read, Random Write, Mixed (70/30 read/write).
- **Repetitions:** 1 warm-up + 3 to 5 measured runs per configuration.
- **Scheduler Restoration:** Original scheduler captured before tests; automatic restoration in `finally` blocks.
