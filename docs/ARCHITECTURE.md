# System Architecture

```mermaid
flowchart TD
    subgraph ConfigLayer ["Configuration Layer"]
        C1["configs/cpu_experiment_matrix.yaml"]
        C2["configs/ml_config.yaml"]
        C3["configs/io_defaults.yaml"]
    end

    subgraph CPUWorkload ["Workload & Feature Layer"]
        WG["WorkloadGenerator (5 Families)"]
        FE["PreExecutionFeatureExtractor (12 Features)"]
    end

    subgraph SimulationCore ["CPU Simulator Core"]
        SIM["CPUSimulator (Deterministic Discrete-Event Engine)"]
        P_FCFS["FCFS Scheduler"]
        P_SJF["SJF Clairvoyant Scheduler"]
        P_PRI["Priority Scheduler"]
        P_RR["Round Robin Scheduler (q=2, 5, 10)"]
    end

    subgraph MetricsAndStorage ["Artifact Store & Registry"]
        MET["calculate_metrics & validation"]
        AST["ArtifactStore (runs/run_id/)"]
        REG["ExperimentRegistry (registry.json)"]
    end

    subgraph MLLayer ["Machine Learning Recommender"]
        DB["DatasetBuilder (Scenario-level)"]
        SPL["Stratified 70/15/15 Scenario Split"]
        TR["ModelTrainer (DecisionTreeClassifier depth<=4)"]
        EXP["Explainability (Rule Path Extraction)"]
        EVAL["Evaluator (Baselines vs Oracle on Test Split)"]
    end

    subgraph IOLab ["Storage I/O Subsystem"]
        HP["host_probe (Sysfs & Hardware Discovery)"]
        FIO_J["fio_jobs (Safe Scratch Target Generator)"]
        FIO_R["fio_runner (Execution & JSON Parser)"]
    end

    subgraph UI ["Research Workbench UI"]
        ST_APP["Streamlit Workbench (app.py)"]
        P_OVERVIEW["Page 1: Overview"]
        P_CPU["Page 2: CPU Lab"]
        P_IO["Page 3: I/O Lab"]
        P_REG["Page 4: Experiment Registry"]
        P_LOG["Page 5: Research Log"]
        P_METH["Page 6: Methodology"]
    end

    C1 --> WG
    WG --> SIM
    SIM --> P_FCFS & P_SJF & P_PRI & P_RR
    P_FCFS & P_SJF & P_PRI & P_RR --> MET
    MET --> AST & REG
    REG --> DB
    WG --> FE
    FE --> DB
    DB --> SPL --> TR --> EXP & EVAL
    HP --> FIO_J --> FIO_R --> REG

    AST & REG & TR & EXP & EVAL & HP & FIO_R --> UI
    UI --> P_OVERVIEW & P_CPU & P_IO & P_REG & P_LOG & P_METH
```

## Architectural Separation of Concerns

1. **Pure Core Simulation (`src/scheduling_lab/core/`):** Contains zero UI or Streamlit dependencies. Implements discrete-event scheduling, lifecycle tracking, and invariant validation. Fully testable in headless CI environments.
2. **Deterministic Schedulers (`src/scheduling_lab/schedulers/`):** Polymorphic implementations behind `BaseScheduler` defining candidate selection and preemption rules.
3. **Leakage-Free Feature Extraction (`src/scheduling_lab/workloads/`):** Extracts 12 pre-execution summary features without touching post-run metrics.
4. **Immutable Experiment Persistence (`src/scheduling_lab/experiments/`):** Each run produces a self-contained, reproducible artifact directory with manifest, scenario, trace, timeline, and metrics.
5. **Explainable ML Engine (`src/scheduling_lab/ml/`):** Strictly scenario-grouped train/val/test partitioning; bounded Decision Tree for human-readable rule paths.
6. **I/O Safety Subsystem (`src/scheduling_lab/io_lab/`):** Enforces disposable scratch-file targeting; guarantees no raw block device access.
7. **Research Workbench Interface (`src/scheduling_lab/ui/`):** Instrument-style Streamlit dashboard reading directly from immutable saved artifacts.
