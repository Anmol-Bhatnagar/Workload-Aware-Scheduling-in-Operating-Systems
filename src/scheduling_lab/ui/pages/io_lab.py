"""
Page 3 — Linux Storage I/O Scheduling Lab.
Safe file-backed fio benchmarks, hardware sysfs discovery, throughput/latency analysis, and cached reference results.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from scheduling_lab.io_lab.fio_runner import FIORunner
from scheduling_lab.io_lab.host_probe import probe_host
from scheduling_lab.reporting.charts import create_io_comparison_bar
from scheduling_lab.ui.components.header import render_header


def render_io_lab_page() -> None:
    render_header(
        title="Linux Storage I/O Scheduling Lab",
        subtitle="Empirical benchmarking of Linux block I/O schedulers under sequential and random workloads",
    )

    probe_data = probe_host()

    # Host & Device Hardware Panel
    st.markdown("<div class='section-header'>Host Environment & Device Discovery (Sysfs Probe)</div>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        st.markdown(
            f"<div class='metric-box'>"
            f"<div class='metric-label'>Operating System & Kernel</div>"
            f"<div class='metric-value' style='font-size: 1.05rem;'>{probe_data['os']['system']} {probe_data['os']['release'][:20]}</div>"
            f"<div class='metric-sub'>Environment: {probe_data['virtualization']['environment_type']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with p_col2:
        st.markdown(
            f"<div class='metric-box'>"
            f"<div class='metric-label'>Compute & Memory</div>"
            f"<div class='metric-value' style='font-size: 1.05rem;'>{probe_data['cpu']['logical_cores']} Cores | {probe_data['memory']['total_gib']} GiB RAM</div>"
            f"<div class='metric-sub'>Processor: {probe_data['cpu']['model'][:30]}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with p_col3:
        fio_stat = "Installed" if probe_data["tools"]["fio_installed"] else "Unavailable on current host"
        fio_pill = "ready" if probe_data["tools"]["fio_installed"] else "warning"
        st.markdown(
            f"<div class='metric-box'>"
            f"<div class='metric-label'>fio Benchmark Engine</div>"
            f"<div class='metric-value' style='font-size: 1.05rem;'>{probe_data['tools'].get('fio_version') or 'fio not found'}</div>"
            f"<div class='metric-sub'><span class='status-pill {fio_pill}'>{fio_stat}</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Safety Notice Banner
    st.info(
        "**Strict Safety Protocol (Mandatory):** Storage benchmarks strictly target a disposable file in "
        "`data/scratch/fio_test.dat`. Under NO circumstances are raw block devices (/dev/sda, /dev/nvme0n1) targeted."
    )

    # Benchmark Controls
    with st.expander("Storage Benchmark Configuration", expanded=True):
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
            workload = st.selectbox(
                "I/O Workload Profile",
                options=["seq_read", "rand_read", "rand_write", "mixed_randrw"],
                format_func=lambda x: {
                    "seq_read": "Sequential Read (128k)",
                    "rand_read": "Random Read (4k)",
                    "rand_write": "Random Write (4k)",
                    "mixed_randrw": "Mixed Read/Write (70/30)",
                }[x],
            )
        with b_col2:
            file_size = st.selectbox("Test File Size", options=[256, 512, 1024], index=1, format_func=lambda x: f"{x} MiB")
        with b_col3:
            runtime = st.number_input("Runtime (seconds)", min_value=5, max_value=30, value=10, step=5)
        with b_col4:
            repetitions = st.number_input("Measured Repetitions", min_value=1, max_value=5, value=3, step=1)

        confirm_safe = st.checkbox(
            "I confirm that benchmarks will execute ONLY on a disposable test file inside data/scratch/ and NOT on a raw storage device.",
            value=False,
        )
        dry_run_choice = st.checkbox("Execute Dry Run Only (validate parameters without running fio)", value=True)

        run_bench_btn = st.button("Launch Storage Benchmark", type="primary", disabled=not confirm_safe)

    if run_bench_btn:
        runner = FIORunner()
        st.write(f"Launching benchmark for workload: `{workload}`...")
        res = runner.run_benchmark(
            workload_id=workload,
            file_size_mib=file_size,
            runtime_seconds=runtime,
            dry_run=dry_run_choice,
        )
        if res.get("status") == "DRY_RUN":
            st.success(f"Dry Run Validated: Target file `{res['target_file']}` and job configuration verified safe.")
        elif res.get("status") == "UNAVAILABLE":
            st.warning(f"Benchmark Status: UNAVAILABLE ({res.get('error_message')})")

    # Cached Linux Reference Study Display
    st.markdown("<div class='section-header'>Linux Storage Scheduler Empirical Benchmark (Reference Study)</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size: 0.85rem; color: #5E6B75; margin-bottom: 12px;'>"
        "<i>Note: Displaying empirical Linux reference benchmark results collected on a dedicated Linux host "
        "(Ubuntu 6.8 kernel, NVMe SSD) across 'none', 'mq-deadline', and 'bfq' schedulers.</i>"
        "</div>",
        unsafe_allow_html=True,
    )

    cached_file = Path("results/tables/cached_linux_io_benchmark.json")
    if cached_file.exists():
        with open(cached_file, "r", encoding="utf-8") as f:
            cached_data = json.load(f)

        bench_df = pd.DataFrame(cached_data["workload_benchmarks"])

        c_tab1, c_tab2, c_tab3 = st.tabs(["Throughput (MiB/s)", "IOPS Performance", "Latency Distributions"])

        with c_tab1:
            fig_bw = px.bar(
                bench_df,
                x="workload_name",
                y="throughput_mib_s",
                color="scheduler",
                barmode="group",
                title="Throughput Across I/O Schedulers (MiB/s — Higher is Better)",
                color_discrete_map={"none": "#147D78", "mq-deadline": "#345F86", "bfq": "#C17A24"},
            )
            fig_bw.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", height=320)
            st.plotly_chart(fig_bw, use_container_width=True)

        with c_tab2:
            fig_iops = px.bar(
                bench_df,
                x="workload_name",
                y="iops",
                color="scheduler",
                barmode="group",
                title="IOPS Across I/O Schedulers (Higher is Better)",
                color_discrete_map={"none": "#147D78", "mq-deadline": "#345F86", "bfq": "#C17A24"},
            )
            fig_iops.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", height=320)
            st.plotly_chart(fig_iops, use_container_width=True)

        with c_tab3:
            st.markdown("**Latency Comparison Across Schedulers (Microseconds — Lower is Better):**")
            lat_table = bench_df[["workload_name", "scheduler", "latency_mean_us", "latency_p95_us", "latency_p99_us"]].copy()
            lat_table.columns = ["Workload", "Scheduler", "Mean Latency (µs)", "p95 Latency (µs)", "p99 Latency (µs)"]
            st.dataframe(lat_table, hide_index=True, use_container_width=True)
