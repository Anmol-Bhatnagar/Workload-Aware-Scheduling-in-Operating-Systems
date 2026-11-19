"""
Custom CSS styles adhering to UI_DESIGN_RULES.md.
Editorial, research-workbench aesthetic with crisp borders and tabular typography.
"""

WORKBENCH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #17232D;
}

code, kbd, samp, pre, .font-mono {
    font-family: 'IBM Plex Mono', 'SFMono-Regular', Consolas, Menlo, monospace !important;
    font-feature-settings: "tnum" 1;
}

/* Main background & margins */
.main .block-container {
    max-width: 1400px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Header & status strip */
.status-bar {
    background-color: #FFFFFF;
    border: 1px solid #D9E0E4;
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 3px;
    font-weight: 500;
    font-size: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
}

.status-pill.ready {
    background-color: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #A5D6A7;
}

.status-pill.warning {
    background-color: #FFF8E1;
    color: #C17A24;
    border: 1px solid #FFE082;
}

.status-pill.neutral {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #CBD5E1;
}

/* Metric callouts */
.metric-box {
    background-color: #FFFFFF;
    border: 1px solid #D9E0E4;
    border-radius: 4px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.metric-label {
    font-size: 0.78rem;
    color: #5E6B75;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    color: #17232D;
    line-height: 1.2;
}

.metric-sub {
    font-size: 0.75rem;
    color: #5E6B75;
    margin-top: 4px;
}

/* Decision tree rule path */
.rule-step {
    border-left: 3px solid #147D78;
    background-color: #F8FAFB;
    padding: 6px 12px;
    margin-bottom: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
}

/* Dataframe & table typography */
.dataframe {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* Section titles */
.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #17232D;
    border-bottom: 1px solid #D9E0E4;
    padding-bottom: 6px;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}
</style>
"""
