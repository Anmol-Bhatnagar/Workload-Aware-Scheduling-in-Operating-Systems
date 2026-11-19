"""
Plotly Chart Generators for the Operating Systems Research Workbench.
Strictly adheres to UI_DESIGN_RULES.md fixed color palette and typography.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from scheduling_lab.core.models import TimelineInterval

POLICY_COLORS = {
    "FCFS": "#7F8C8D",       # Slate Grey
    "SJF": "#147D78",        # Deep Research Teal
    "RR_Q2": "#E09436",      # Light Amber
    "RR_Q5": "#C17A24",      # Warm Amber
    "RR_Q10": "#965912",     # Dark Amber
    "PRIORITY": "#345F86",   # Slate Blue
    "ML": "#1B4D3E",         # Forest Jade
    "Oracle": "#5E6B75",     # Muted Steel
    "IDLE": "#D9E0E4",       # Muted Canvas Grey
}

PROCESS_COLORS = [
    "#147D78", "#345F86", "#C17A24", "#34765A", "#6D4C41",
    "#546E7A", "#7B1FA2", "#C2185B", "#00838F", "#2E7D32",
    "#D84315", "#455A64", "#00695C", "#283593", "#4E342E",
    "#1565C0", "#004D40", "#AD1457", "#37474F", "#827717",
]


def create_gantt_chart(timeline: List[TimelineInterval], title: str = "CPU Execution Timeline") -> go.Figure:
    """Generate Gantt execution timeline showing process execution and idle gaps."""
    if not timeline:
        fig = go.Figure()
        fig.update_layout(title="No execution intervals available")
        return fig

    # Build unique PID color mapping
    unique_pids = sorted(list({t.pid for t in timeline if t.pid != "IDLE"}))
    pid_color_map = {pid: PROCESS_COLORS[i % len(PROCESS_COLORS)] for i, pid in enumerate(unique_pids)}
    pid_color_map["IDLE"] = "#D9E0E4"

    fig = go.Figure()

    for item in timeline:
        color = pid_color_map.get(item.pid, "#7F8C8D")
        hover = (
            f"<b>{item.pid}</b><br>"
            f"Interval: [{item.start_time}, {item.end_time})<br>"
            f"Duration: {item.duration} ticks<br>"
            f"Type: {item.interval_type}"
        )
        fig.add_trace(
            go.Bar(
                x=[item.duration],
                y=[item.pid],
                base=[item.start_time],
                orientation="h",
                marker=dict(color=color, line=dict(color="#17232D", width=1)),
                hovertemplate=hover + "<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(family="IBM Plex Sans, sans-serif", size=15, color="#17232D")),
        xaxis=dict(
            title="Simulation Time (Ticks)",
            tickmode="linear",
            dtick=max(1, int((timeline[-1].end_time // 20) + 1)),
            gridcolor="#E2E8F0",
            zerolinecolor="#CBD5E1",
        ),
        yaxis=dict(title="Process ID", categoryorder="category descending"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=320,
        margin=dict(l=60, r=20, t=40, b=40),
    )
    return fig


def create_policy_comparison_bar(
    metrics_by_policy: Dict[str, float],
    metric_name: str = "Average Response Time",
    unit: str = "ticks",
) -> go.Figure:
    """Generate comparative horizontal bar chart for candidate policies."""
    policies = list(metrics_by_policy.keys())
    values = [metrics_by_policy[p] for p in policies]
    colors = [POLICY_COLORS.get(p, "#345F86") for p in policies]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=policies,
            orientation="h",
            marker=dict(color=colors, line=dict(color="#17232D", width=1)),
            hovertemplate="<b>%{y}</b>: %{x:.2f} " + unit + "<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text=f"Policy Comparison: {metric_name} ({unit})",
            font=dict(family="IBM Plex Sans, sans-serif", size=14, color="#17232D"),
        ),
        xaxis=dict(title=f"{metric_name} ({unit})", gridcolor="#E2E8F0"),
        yaxis=dict(categoryorder="total descending"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=280,
        margin=dict(l=80, r=20, t=40, b=40),
    )
    return fig


def create_io_comparison_bar(
    data: List[Dict[str, Any]],
    x_metric: str = "iops",
    title: str = "I/O Benchmark Performance",
) -> go.Figure:
    """Generate comparative chart for storage I/O benchmarks."""
    df = pd.DataFrame(data)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No I/O data available")
        return fig

    fig = px.bar(
        df,
        x=x_metric,
        y="workload_id",
        color="scheduler",
        barmode="group",
        title=title,
        color_discrete_sequence=["#147D78", "#345F86", "#C17A24", "#34765A"],
    )
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=320,
        margin=dict(l=80, r=20, t=40, b=40),
    )
    return fig
