"""
Shared header and system status bar component.
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st

from scheduling_lab.experiments.registry import ExperimentRegistry
from scheduling_lab.ml.recommender import PolicyRecommender


def render_header(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<div style='color: #5E6B75; margin-top: -12px; margin-bottom: 16px; font-size: 0.95rem;'>{subtitle}</div>", unsafe_allow_html=True)

    # Status strip
    recommender = PolicyRecommender()
    registry = ExperimentRegistry()
    runs = registry.get_runs()
    latest_run = runs[-1] if runs else None

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            "<div class='status-bar'><div><b>CPU Simulator</b></div>"
            "<span class='status-pill ready'>READY</span></div>",
            unsafe_allow_html=True,
        )

    with col2:
        ml_status = (
            "<span class='status-pill ready'>TRAINED</span>"
            if recommender.is_available
            else "<span class='status-pill warning'>NOT TRAINED</span>"
        )
        st.markdown(
            f"<div class='status-bar'><div><b>ML Model</b></div>{ml_status}</div>",
            unsafe_allow_html=True,
        )

    with col3:
        host_probe_file = Path("results/host_probe.json")
        io_status = (
            "<span class='status-pill neutral'>LIMITED (PROBED)</span>"
            if host_probe_file.exists()
            else "<span class='status-pill warning'>NOT PROBED</span>"
        )
        st.markdown(
            f"<div class='status-bar'><div><b>Linux I/O</b></div>{io_status}</div>",
            unsafe_allow_html=True,
        )

    with col4:
        run_text = f"{len(runs)} RUNS" if runs else "NO RUNS"
        st.markdown(
            f"<div class='status-bar'><div><b>Registry</b></div>"
            f"<span class='status-pill neutral'>{run_text}</span></div>",
            unsafe_allow_html=True,
        )
