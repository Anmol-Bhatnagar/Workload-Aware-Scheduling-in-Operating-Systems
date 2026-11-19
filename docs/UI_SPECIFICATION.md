# Research Dashboard UI Specification

## 1. Sidebar Navigation
Order of pages is strictly defined:
1. **Overview**: Executive research status, global comparative summary, active recommendation.
2. **CPU Scheduling Lab**: Interactive scenario generator, Gantt execution timeline, policy comparison table, per-process drilldown, decision-tree explanation.
3. **I/O Scheduling Lab**: Linux host hardware probe, safe file-backed `fio` benchmark execution, scheduler throughput/latency comparison.
4. **Experiment Registry**: Filterable, searchable archive of all past runs with raw artifact viewer and download actions.
5. **Research Log**: Chronological research logs, empirical observations, hypothesis evaluations, and reviewer notes.
6. **Methodology & Reproducibility**: Research questions, metric mathematical formulations, split parameters, hardware specs, and CLI reproduction commands.

---

## 2. Page Specifications

### Page 1 — Overview
- **Header:** "Scheduling Research Workbench" — Workload-aware CPU and Linux I/O scheduling experiments.
- **Environment Status Strip:**
  - CPU Simulator: `READY`
  - ML Model: `TRAINED` or `NOT TRAINED`
  - Linux I/O: `AVAILABLE`, `LIMITED` (e.g. single scheduler/WSL), or `NOT PROBED`
  - Latest Run ID & Timestamp
- **Comparative Chart:** Grouped bar chart comparing FCFS, SJF, RR, Priority, and ML Selector across the chosen metric (Response Time, Turnaround, Waiting, Context Switches).
- **Active Recommendation Widget:** Shows current model suggestion, input workload profile, and decision path.
- **Recent Runs Table:** Most recent 5 experiments with run status pills.
- **Research Questions Status:** Status of RQ1–RQ4 (`Not Started`, `In Progress`, `Evidence Collected`).

### Page 2 — CPU Scheduling Lab
- **Input Controls:**
  - Workload Profile: CPU-Bound, I/O-Bound, Interactive, Mixed, Bursty Arrivals, Custom.
  - Process Count: Bounded slider/input (5–25, default 10).
  - Random Seed: Integer input.
  - Policy Selection: Checkboxes for FCFS, SJF, Priority, Round Robin (with quanta inputs q=2, 5, 10).
  - Context-Switch Cost: Simulator parameter input (default 0).
  - Actions: `Run Selected Baselines`, `Run ML Recommendation`, `Run Full Comparison`.
- **Results View:**
  - **Gantt Timeline:** Interactive Plotly timeline showing process execution, I/O waits, and idle time on a common tick axis.
  - **Summary Table:** Average Turnaround, Response, Ready Wait, Context Switches, CPU Utilisation (%), Throughput (proc/tick), Composite Cost.
  - **Per-Process Table:** Process ID, Arrival, First Start, Finish, Ready Wait, Blocked Wait, Response, Turnaround.
  - **Decision Path:** Explainable feature vector and decision tree branch leading to the recommendation.

### Page 3 — I/O Scheduling Lab
- **Host & Device Probe:**
  - Kernel version, CPU, RAM, block device, filesystem, mount point.
  - Available schedulers (e.g. `[none] mq-deadline bfq`).
  - Active scheduler indicator.
- **Safety & Benchmark Configuration:**
  - Scratch target path: `data/scratch/fio_test.dat`.
  - Target file size (default 512 MiB, max 1 GiB).
  - Workload pattern: Sequential Read, Random Read, Random Write, Mixed (70/30).
  - Safety Confirmation: Mandatory checkbox confirming safe file-backed testing before any write benchmark.
- **Results View:**
  - Throughput (MiB/s) and IOPS bar charts.
  - Latency comparison (Mean, p95, p99).
  - Repetition spread table (Mean $\pm$ Std across repeats).

### Page 4 — Experiment Registry
- Table of all historical runs (`run_id`, `timestamp`, `type`, `workload`, `policy`, `status`).
- Drilldown modal / pane showing:
  - `run_manifest.json`
  - `scenario.json`
  - `event_trace.jsonl`
  - Raw `timeline.csv` and `process_metrics.csv`
  - `summary_metrics.json`
- Export button to download runs as ZIP/JSON.

### Page 5 — Research Log
- Chronological logs linked directly to experiment run IDs.
- Research fields: Hypothesis, Workload Family, Observations, Interpretation, Limitations, Conclusion Status.

### Page 6 — Methodology & Reproducibility
- Mathematical definitions of metrics.
- Complete feature list with formulas.
- Frozen composite cost weight configuration.
- One-click copy CLI reproduction commands.
