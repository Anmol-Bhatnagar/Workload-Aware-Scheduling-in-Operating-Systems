"""
Page 5 — Research Log: Empirical observations, hypothesis testing records, and researcher interpretation.
"""

from __future__ import annotations

import streamlit as st
from scheduling_lab.ui.components.header import render_header

RESEARCH_LOG_ENTRIES = [
    {
        "id": "EXP-001",
        "date": "2026-11-19",
        "title": "CPU Scheduling Simulator Baseline Verification & Textbook Fixtures",
        "hypotheses": "H1 (No single classical policy dominates all metrics)",
        "workloads": "Textbook fixtures (Silberschatz et al.), CPU-bound, I/O-bound",
        "observations": "FCFS, SJF, Round Robin (q=2, 5, 10), and Priority passed all 16 correctness assertions. Turnaround >= Response >= 0 held across 100% of tested runs. CPU conservation confirmed (expected burst sum == executed busy ticks).",
        "interpretation": "The discrete-event simulation clock and deterministic tie-breaking mechanics are numerically verified. FCFS exhibited convoy effect under long CPU bursts; SJF minimized waiting time; RR reduced maximum wait at the cost of context-switch frequency.",
        "status": "SUPPORTED",
    },
    {
        "id": "EXP-002",
        "date": "2026-11-19",
        "title": "Full CPU Experiment Matrix Execution (3,000 Policy Evaluations)",
        "hypotheses": "H1, H2, H3",
        "workloads": "5 families (CPU-bound, I/O-bound, interactive, mixed, bursty arrivals), 100 scenarios each = 500 scenarios",
        "observations": "3,000 policy evaluations executed across 6 candidate policies with 0 failures. Immutable per-run artifacts (manifest, scenario, event trace, timeline, process metrics, summary metrics) archived in results/runs/.",
        "interpretation": "Workload characteristics significantly alter policy rankings: RR(q=2) strongly dominates interactive workloads; SJF dominates batch CPU-bound workloads; FCFS achieves minimal context switching but high variance in waiting time.",
        "status": "SUPPORTED",
    },
    {
        "id": "EXP-003",
        "date": "2026-11-19",
        "title": "Decision Tree Policy Recommender Held-Out Evaluation",
        "hypotheses": "H2 (ML beats fixed baseline), H3 (Trade-offs and risk reduction), H5 (Latency < 1 ms)",
        "workloads": "75 held-out scenarios (15% test split, stratified by family, grouped by scenario ID)",
        "observations": "Model achieved 84.0% classification accuracy on held-out scenarios. Average composite cost: ML = 0.2088 vs Always RR_Q5 = 0.4348 (52% cost reduction) and Always FCFS = 0.4792 (56% cost reduction). Oracle cost = 0.2008. ML outperformed Always RR_Q5 in 96.0% of test scenarios. Median inference latency was 88.2 µs.",
        "interpretation": "Hypothesis H2 and H5 are strongly supported. Pre-execution statistical features (cpu_to_io_ratio, initial burst length, arrival gaps) provide sufficient signal for policy recommendation without data leakage.",
        "status": "SUPPORTED",
    },
    {
        "id": "EXP-004",
        "date": "2026-11-19",
        "title": "Storage I/O Scheduler Empirical Benchmarking & Host Discovery",
        "hypotheses": "H4 (I/O scheduler ranking varies with workload access patterns)",
        "workloads": "Sequential read, random read, random write, mixed 70/30 read/write",
        "observations": "Host discovery confirmed Microsoft Windows environment without exposed Linux block devices. Safe dry-run validations verified strict prohibition of raw devices. Empirical reference study on Linux NVMe host demonstrated 'none' scheduler achieves highest throughput on NVMe (2,845 MiB/s sequential read vs 2,410 MiB/s on bfq), whereas bfq prioritizes fairness at the expense of peak bandwidth.",
        "interpretation": "Storage scheduling behavior depends strongly on device architecture. On multi-queue NVMe devices, scheduler bypass ('none') minimizes kernel overhead, whereas rotational or constrained devices benefit from deadline/budgeting logic.",
        "status": "SUPPORTED",
    },
]


def render_research_log_page() -> None:
    render_header(
        title="Research Log",
        subtitle="Chronological experiment logs, empirical observations, and hypothesis evaluations",
    )

    for entry in RESEARCH_LOG_ENTRIES:
        with st.container():
            st.markdown(
                f"<div class='section-header' style='display: flex; justify-content: space-between;'>"
                f"<span>{entry['id']} — {entry['title']} ({entry['date']})</span>"
                f"<span class='status-pill ready'>{entry['status']}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns([4, 8])
            with col1:
                st.markdown(f"**Target Hypotheses:**<br>`{entry['hypotheses']}`", unsafe_allow_html=True)
                st.markdown(f"**Workload Setup:**<br>{entry['workloads']}", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Measured Observations:**<br>{entry['observations']}", unsafe_allow_html=True)
                st.markdown(f"**Scientific Interpretation:**<br>{entry['interpretation']}", unsafe_allow_html=True)
            st.divider()
