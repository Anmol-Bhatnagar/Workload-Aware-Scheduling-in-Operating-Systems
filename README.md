# Intelligent Workload-Aware Scheduling Lab

**Comparative Study of CPU and Storage I/O Resource Management**

## 1. Project Overview

This repository contains an experimental research workbench for investigating workload-aware resource scheduling in operating systems:
1. **CPU Scheduling Simulator (Primary Focus):** A discrete-event CPU scheduling simulation environment implementing classical scheduling algorithms (FCFS, SJF, Round Robin with configurable quanta, Non-preemptive Priority), controlled synthetic workload generators (CPU-bound, I/O-bound, interactive, mixed, bursty arrivals), and an interpretable Decision Tree policy recommender evaluated against fixed baselines on held-out scenarios.
2. **Linux Storage I/O Benchmarking (Add-on Study):** A safe, reproducible `fio`-based empirical benchmark evaluating Linux block I/O schedulers across sequential and random access workloads on disposable file targets.
3. **Research Dashboard:** An editorial, instrument-grade Streamlit research interface linking every chart, table, and conclusion to raw, immutable experiment runs.

> **Research Integrity Notice:** This simulator is an educational and experimental research tool. It does not modify the live Linux kernel CPU scheduler, does not implement EEVDF, and does not claim that synthetic workloads represent production OS telemetry. All findings are derived strictly from reproducible experiment logs.

## 2. Directory Structure

```text
├── configs/             # YAML configurations for workloads, policies, and ML
├── data/
│   ├── generated/       # Generated CPU scenario definitions
│   └── scratch/         # Disposable test files for I/O tests (git-ignored)
├── docs/                # Research protocol, specifications, and architecture
├── models/              # Saved model checkpoints and metadata
├── results/
│   ├── runs/            # Immutable per-run artifacts (manifest, trace, metrics)
│   ├── tables/          # Summary comparison tables
│   └── figures/         # Rendered publication figures
├── scripts/             # Reproducible CLI scripts for matrix runs and training
├── src/scheduling_lab/  # Core Python package
└── tests/               # Unit, integration, and acceptance tests
```

## 3. Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate virtual environment (Linux / macOS)
source .venv/bin/activate

# Install package and development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest -q
```

### Running Experiments via CLI

```bash
# 1. Run CPU pilot experiment
python scripts/run_cpu_suite.py --config configs/cpu_defaults.yaml --pilot

# 2. Run full CPU experiment matrix
python scripts/run_cpu_suite.py --config configs/cpu_experiment_matrix.yaml

# 3. Train the policy recommender
python scripts/train_recommender.py --config configs/ml_config.yaml

# 4. Evaluate on held-out test scenarios
python scripts/train_recommender.py --evaluate-only --split test

# 5. Probe host for Linux I/O capabilities (read-only)
python scripts/run_io_probe.py --output results/host_probe.json

# 6. Launch Research Dashboard
streamlit run src/scheduling_lab/app.py
```

## 4. Documentation References

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Project Status](docs/PROJECT_STATUS.md)
- [Task Checklist](docs/TASK_CHECKLIST.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Research Protocol](docs/RESEARCH_PROTOCOL.md)
- [UI Design Rules](docs/UI_DESIGN_RULES.md)
- [UI Specification](docs/UI_SPECIFICATION.md)
- [Research Log](docs/research_log.md)
