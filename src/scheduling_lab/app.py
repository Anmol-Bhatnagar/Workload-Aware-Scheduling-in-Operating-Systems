"""
Main Streamlit Application Entrypoint: Operating Systems Research Workbench.
"""

from __future__ import annotations

import streamlit as st

from scheduling_lab.ui.pages.cpu_lab import render_cpu_lab_page
from scheduling_lab.ui.pages.experiments import render_experiments_page
from scheduling_lab.ui.pages.io_lab import render_io_lab_page
from scheduling_lab.ui.pages.methodology import render_methodology_page
from scheduling_lab.ui.pages.overview import render_overview_page
from scheduling_lab.ui.pages.research_log import render_research_log_page
from scheduling_lab.ui.styles import WORKBENCH_CSS

# Page configuration
st.set_page_config(
    page_title="Scheduling Research Workbench",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply research workbench CSS
st.markdown(WORKBENCH_CSS, unsafe_allow_html=True)

# Sidebar Navigation (strictly ordered per specification)
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 2px; color: #17232D;'>OS Research Lab</h3>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.8rem; color: #5E6B75; margin-bottom: 20px;'>Operating Systems for Smart Tech</div>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "Overview",
            "CPU Scheduling Lab",
            "I/O Scheduling Lab",
            "Experiment Registry",
            "Research Log",
            "Methodology & Reproducibility",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.75rem; color: #5E6B75; line-height: 1.4;'>"
        "<b>Operating Systems Research Workbench</b><br>"
        "Comparative Study of CPU and Storage I/O Resource Management<br>"
        "Version 1.0.0"
        "</div>",
        unsafe_allow_html=True,
    )

# Page Dispatch
if page == "Overview":
    render_overview_page()
elif page == "CPU Scheduling Lab":
    render_cpu_lab_page()
elif page == "I/O Scheduling Lab":
    render_io_lab_page()
elif page == "Experiment Registry":
    render_experiments_page()
elif page == "Research Log":
    render_research_log_page()
elif page == "Methodology & Reproducibility":
    render_methodology_page()
