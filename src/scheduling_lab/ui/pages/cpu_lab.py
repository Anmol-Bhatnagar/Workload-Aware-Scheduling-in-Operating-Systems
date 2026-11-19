"""
Page 2 — CPU Scheduling Lab: Interactive simulator, Gantt timelines, metrics, and policy explanations.
"""

from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from scheduling_lab.core.simulator import CPUSimulator, SimulationResult
from scheduling_lab.ml.objective import DEFAULT_WEIGHTS, compute_scenario_costs
from scheduling_lab.ml.recommender import PolicyRecommender
from scheduling_lab.reporting.charts import create_gantt_chart
from scheduling_lab.reporting.tables import format_metrics_comparison_table, format_process_details_table
from scheduling_lab.schedulers.registry import create_scheduler
from scheduling_lab.ui.components.header import render_header
from scheduling_lab.workloads.generator import WorkloadGenerator
from scheduling_lab.workloads.profiles import WorkloadFamily


def render_cpu_lab_page() -> None:
    render_header(
        title="CPU Scheduling Lab",
        subtitle="Controlled discrete-event simulation of classical CPU scheduling policies and ML recommendation",
    )

    # Top Configuration Panel
    with st.expander("Workload & Simulation Parameters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            family_choice = st.selectbox(
                "Workload Family",
                options=["mixed", "cpu_bound", "io_bound", "interactive", "bursty_arrivals"],
                index=0,
                format_func=lambda x: x.replace("_", " ").title(),
            )
        with col2:
            process_count = st.slider("Process Count", min_value=5, max_value=25, value=10, step=1)
        with col3:
            seed = st.number_input("Random Seed", min_value=1, max_value=999999, value=42, step=1)
        with col4:
            cs_cost = st.number_input("Context Switch Cost (ticks)", min_value=0, max_value=5, value=0, step=1)

        st.markdown("**Candidate Policies to Compare:**")
        pol_col1, pol_col2, pol_col3, pol_col4, pol_col5, pol_col6 = st.columns(6)
        run_fcfs = pol_col1.checkbox("FCFS", value=True)
        run_sjf = pol_col2.checkbox("SJF (Clairvoyant)", value=True)
        run_pri = pol_col3.checkbox("Priority", value=True)
        run_rr2 = pol_col4.checkbox("RR (q=2)", value=True)
        run_rr5 = pol_col5.checkbox("RR (q=5)", value=True)
        run_rr10 = pol_col6.checkbox("RR (q=10)", value=True)

        action_col1, action_col2, _ = st.columns([2, 2, 4])
        run_btn = action_col1.button("Run Simulation Comparison", type="primary", use_container_width=True)

    # Generate scenario
    scenario_data = WorkloadGenerator.generate_scenario(
        family=family_choice,
        process_count=process_count,
        seed=int(seed),
        scenario_id=f"{family_choice}_s{seed}_n{process_count}",
    )
    processes = WorkloadGenerator.load_scenario_processes(scenario_data)

    # Run ML recommender
    recommender = PolicyRecommender()
    rec_result = recommender.recommend(processes)

    # State storage for interactive execution
    if run_btn or "sim_results" not in st.session_state or st.session_state.get("current_seed") != seed:
        st.session_state["current_seed"] = seed
        selected_candidates = []
        if run_fcfs:
            selected_candidates.append(("FCFS", "fcfs", {}))
        if run_sjf:
            selected_candidates.append(("SJF", "sjf", {}))
        if run_pri:
            selected_candidates.append(("PRIORITY", "priority", {"lower_is_higher": True}))
        if run_rr2:
            selected_candidates.append(("RR_Q2", "rr", {"quantum": 2, "name": "RR_Q2"}))
        if run_rr5:
            selected_candidates.append(("RR_Q5", "rr", {"quantum": 5, "name": "RR_Q5"}))
        if run_rr10:
            selected_candidates.append(("RR_Q10", "rr", {"quantum": 10, "name": "RR_Q10"}))

        sim_results: Dict[str, SimulationResult] = {}
        for cand_name, p_type, p_params in selected_candidates:
            sched = create_scheduler(p_type, **p_params)
            sim = CPUSimulator(scheduler=sched, context_switch_cost=int(cs_cost))
            sim_res = sim.run(
                process_workload=processes,
                scenario_id=scenario_data["scenario_id"],
                seed=int(seed),
                validate=True,
            )
            sim_results[cand_name] = sim_res

        st.session_state["sim_results"] = sim_results

    sim_results = st.session_state.get("sim_results", {})

    # Display Recommender Panel
    st.markdown("<div class='section-header'>Workload-Aware Policy Recommender</div>", unsafe_allow_html=True)
    rec_col1, rec_col2 = st.columns([5, 7])

    with rec_col1:
        st.markdown(
            f"<div class='metric-box'>"
            f"<div class='metric-label'>Recommended Policy</div>"
            f"<div class='metric-value' style='color: #147D78;'>{rec_result['recommended_policy']}</div>"
            f"<div class='metric-sub'>Workload profile: {family_choice.replace('_', ' ').title()} | N = {process_count}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if rec_result.get("is_fallback"):
            st.warning(f"Notice: {rec_result.get('fallback_reason')}")

    with rec_col2:
        if rec_result.get("explanation"):
            exp = rec_result["explanation"]
            st.markdown(f"**Decision Tree Rule Path (Confidence: {exp.get('confidence', 0)*100:.1f}%):**")
            for step in exp.get("decision_path", []):
                st.markdown(f"<div class='rule-step'>Rule: <code>{step['rule_text']}</code></div>", unsafe_allow_html=True)

    if sim_results:
        # Comparison Table
        st.markdown("<div class='section-header'>Performance Summary Across Policies</div>", unsafe_allow_html=True)
        metrics_dict = {name: res.metrics.to_dict() for name, res in sim_results.items()}
        costs_dict = compute_scenario_costs(metrics_dict, weights=DEFAULT_WEIGHTS)
        summary_df = format_metrics_comparison_table(metrics_dict, costs_dict)
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

        # Timeline Gantt Chart
        st.markdown("<div class='section-header'>Execution Timeline (Gantt)</div>", unsafe_allow_html=True)
        inspect_policy = st.selectbox(
            "Select Policy Timeline to Inspect",
            options=list(sim_results.keys()),
            index=0,
        )
        selected_res = sim_results[inspect_policy]
        gantt_fig = create_gantt_chart(
            timeline=selected_res.timeline,
            title=f"CPU Execution Timeline — {inspect_policy} (Scenario: {scenario_data['scenario_id']})",
        )
        st.plotly_chart(gantt_fig, use_container_width=True)

        # Per-Process Lifecycle Details
        st.markdown(f"<div class='section-header'>Per-Process Lifecycle Details ({inspect_policy})</div>", unsafe_allow_html=True)
        proc_df = format_process_details_table([p.to_dict() for p in selected_res.processes])
        st.dataframe(proc_df, hide_index=True, use_container_width=True)
