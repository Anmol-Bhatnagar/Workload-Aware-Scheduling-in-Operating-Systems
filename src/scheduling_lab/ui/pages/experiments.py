"""
Page 4 — Experiment Registry: Complete searchable run index, artifact inspector, and data export.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from scheduling_lab.experiments.registry import ExperimentRegistry
from scheduling_lab.reporting.exports import export_dataframe_csv, zip_run_artifacts
from scheduling_lab.ui.components.header import render_header


def render_experiments_page() -> None:
    render_header(
        title="Experiment Registry",
        subtitle="Searchable archive of all benchmark runs with full artifact traceability and raw file downloads",
    )

    registry = ExperimentRegistry()
    runs = registry.get_runs()

    if not runs:
        st.info("No experiment runs registered. Run python scripts/run_cpu_suite.py to generate benchmarks.")
        return

    # Filters
    st.markdown("<div class='section-header'>Search & Filter Runs</div>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    types = sorted(list({r.get("experiment_type", "CPU") for r in runs}))
    statuses = sorted(list({r.get("status", "COMPLETED") for r in runs}))
    families = sorted(list({r.get("workload_family", "unknown") for r in runs}))
    policies = sorted(list({r.get("policy", "unknown") for r in runs}))

    with f_col1:
        type_filter = st.selectbox("Experiment Type", options=["All"] + types)
    with f_col2:
        family_filter = st.selectbox("Workload Family", options=["All"] + families)
    with f_col3:
        policy_filter = st.selectbox("Policy", options=["All"] + policies)
    with f_col4:
        status_filter = st.selectbox("Status", options=["All"] + statuses)

    filtered_runs = runs
    if type_filter != "All":
        filtered_runs = [r for r in filtered_runs if r.get("experiment_type") == type_filter]
    if family_filter != "All":
        filtered_runs = [r for r in filtered_runs if r.get("workload_family") == family_filter]
    if policy_filter != "All":
        filtered_runs = [r for r in filtered_runs if r.get("policy") == policy_filter]
    if status_filter != "All":
        filtered_runs = [r for r in filtered_runs if r.get("status") == status_filter]

    st.markdown(f"**Showing {len(filtered_runs)} of {len(runs)} total runs**")

    # Display Table
    table_rows = []
    for r in filtered_runs:
        m = r.get("summary_metrics", {})
        table_rows.append({
            "Run ID": r.get("run_id"),
            "Timestamp": r.get("timestamp")[:19],
            "Type": r.get("experiment_type"),
            "Family": r.get("workload_family"),
            "Policy": r.get("policy"),
            "Makespan": m.get("makespan", "-"),
            "Avg Wait (t)": round(m.get("avg_waiting_time", 0), 2) if "avg_waiting_time" in m else "-",
            "Avg Resp (t)": round(m.get("avg_response_time", 0), 2) if "avg_response_time" in m else "-",
            "Status": r.get("status"),
        })

    runs_df = pd.DataFrame(table_rows)
    st.dataframe(runs_df, hide_index=True, use_container_width=True)

    # Export CSV of registry
    csv_str = export_dataframe_csv(runs_df)
    st.download_button(
        "Download Registry Table (CSV)",
        data=csv_str,
        file_name="experiment_registry.csv",
        mime="text/csv",
    )

    # Artifact Drilldown
    st.markdown("<div class='section-header'>Inspect Run Artifacts</div>", unsafe_allow_html=True)
    all_run_ids = [r["Run ID"] for r in table_rows]
    selected_run_id = st.selectbox("Select Run ID to Inspect", options=all_run_ids, index=0)

    if selected_run_id:
        run_folder = Path("results/runs") / selected_run_id
        if run_folder.exists():
            art_col1, art_col2 = st.columns([8, 4])

            with art_col2:
                # Zip download
                zip_bytes = zip_run_artifacts(run_folder)
                st.download_button(
                    label=f"Download Run Artifacts (ZIP)",
                    data=zip_bytes,
                    file_name=f"{selected_run_id}.zip",
                    mime="application/zip",
                )

            with art_col1:
                tab_man, tab_sum, tab_trace, tab_tl = st.tabs(["Manifest", "Summary Metrics", "Event Trace (Head)", "Timeline"])

                with tab_man:
                    man_file = run_folder / "run_manifest.json"
                    if man_file.exists():
                        with open(man_file, "r", encoding="utf-8") as f:
                            st.json(json.load(f))

                with tab_sum:
                    sum_file = run_folder / "summary_metrics.json"
                    if sum_file.exists():
                        with open(sum_file, "r", encoding="utf-8") as f:
                            st.json(json.load(f))

                with tab_trace:
                    trace_file = run_folder / "event_trace.jsonl"
                    if trace_file.exists():
                        lines = []
                        with open(trace_file, "r", encoding="utf-8") as f:
                            for _ in range(15):
                                line = f.readline()
                                if line:
                                    lines.append(json.loads(line))
                        st.dataframe(pd.DataFrame(lines), hide_index=True, use_container_width=True)

                with tab_tl:
                    tl_file = run_folder / "timeline.csv"
                    if tl_file.exists():
                        tl_df = pd.read_csv(tl_file)
                        st.dataframe(tl_df, hide_index=True, use_container_width=True)
