"""
Page 6 — Methodology & Reproducibility: Scientific formulations, protocol details, and exact CLI reproduction commands.
"""

from __future__ import annotations

import streamlit as st
from scheduling_lab.ui.components.header import render_header


def render_methodology_page() -> None:
    render_header(
        title="Methodology & Reproducibility",
        subtitle="Formal research protocol, metric definitions, model specifications, and CLI reproduction commands",
    )

    t1, t2, t3, t4 = st.tabs(["Research Protocol & Hypotheses", "Metric Formulations", "Model & Features", "CLI Reproduction Commands"])

    with t1:
        st.markdown("### Formal Research Hypotheses")
        st.markdown("""
        - **H1 (Policy Diversity):** No single classical CPU scheduling policy dominates across all workload families and performance metrics.
        - **H2 (ML Superiority):** A Decision Tree model trained on pre-execution workload statistical features achieves lower average composite cost on held-out test scenarios than fixed-policy baselines (Always FCFS, Always RR_Q5).
        - **H3 (Trade-off & Risk Reduction):** The workload-aware selector does not achieve lowest cost on 100% of individual scenarios; its primary utility lies in risk minimization across heterogeneous workload mixes.
        - **H4 (Storage I/O Access Dynamics):** Measured Linux block I/O scheduler performance varies with workload access patterns (sequential vs. random).
        - **H5 (Decision Latency):** Model inference latency is under 1 millisecond, negligible compared to simulated workload execution duration, but tracked separately.
        """)

    with t2:
        st.markdown("### Metric Mathematical Formulations")
        st.latex(r"T_{turnaround} = T_{completion} - T_{arrival}")
        st.latex(r"T_{response} = T_{first\_dispatch} - T_{arrival}")
        st.latex(r"T_{ready\_wait} = \sum_{t} \mathbb{I}(\text{State}(t) = \text{READY})")
        st.latex(r"\text{CPU Utilisation} = \frac{\sum \text{Busy Ticks}}{\text{Makespan}} \times 100\%")
        st.markdown("### Composite Cost Objective Function")
        st.latex(r"\text{Cost}(s, p) = 0.30 \cdot \hat{T}_{resp} + 0.25 \cdot \hat{T}_{wait} + 0.20 \cdot \hat{T}_{ta} + 0.15 \cdot \hat{CS} + 0.10 \cdot \hat{U}_{cost}")
        st.markdown(r"Where each metric $\hat{M}$ is min-max normalized across candidate policies evaluated on the identical workload scenario.")

    with t3:
        st.markdown("### 12 Pre-Execution Feature Specifications")
        st.markdown(r"""
        1. `process_count`: Total number of processes in scenario.
        2. `mean_initial_burst`: Mean duration of first CPU burst.
        3. `std_initial_burst`: Standard deviation of first CPU bursts.
        4. `burst_cv`: Coefficient of variation across all CPU bursts ($\sigma / \mu$).
        5. `mean_io_wait`: Mean duration of simulated I/O waits.
        6. `multi_burst_ratio`: Proportion of processes with $>1$ CPU burst.
        7. `cpu_to_io_ratio`: Total expected CPU ticks / (Total expected I/O wait ticks + 1).
        8. `mean_arrival_gap`: Mean time gap between successive process arrivals.
        9. `std_arrival_gap`: Standard deviation of arrival gaps.
        10. `short_burst_ratio`: Proportion of CPU bursts $\le 3$ ticks.
        11. `priority_std`: Standard deviation of assigned priorities.
        12. `arrival_burstiness`: Peak arrival density in any 5-tick sliding window / total processes.
        """)

    with t4:
        st.markdown("### Reproduce Experiments from Command Line")
        st.code("""
# 1. Run CPU pilot experiment (25 scenarios, 150 runs)
python scripts/run_cpu_suite.py --pilot

# 2. Run full CPU experiment matrix (500 scenarios, 3000 runs)
python scripts/run_cpu_suite.py --config configs/cpu_experiment_matrix.yaml

# 3. Train policy recommender on 70% train split and evaluate on 15% held-out test split
python scripts/train_recommender.py --config configs/ml_config.yaml

# 4. Run sensitivity analysis under alternative weight profile
python scripts/train_recommender.py --run-sensitivity

# 5. Probe host for Linux I/O capabilities (read-only)
python scripts/run_io_probe.py --output results/host_probe.json

# 6. Run safe storage benchmark dry-run
python scripts/run_fio_suite.py --config configs/io_defaults.yaml --confirm-scratch-file --dry-run

# 7. Launch this Research Dashboard
streamlit run src/scheduling_lab/app.py
        """, language="bash")
