# Task Checklist

All states must strictly follow: `NOT STARTED`, `IN PROGRESS`, `BLOCKED`, `COMPLETE`, `NOT APPLICABLE`.

## Phase 0 — Repository and Research Setup
- [x] **P0.1** Create the repository structure and Python package. `COMPLETE`
- [x] **P0.2** Add dependency specification, lock/version record, `.gitignore` and Streamlit config. `COMPLETE`
- [x] **P0.3** Add `README.md`, `PROJECT_STATUS.md`, `TASK_CHECKLIST.md`, `DECISIONS.md`. `COMPLETE`
- [x] **P0.4** Write `RESEARCH_PROTOCOL.md` with RQs, hypotheses, metrics, workloads, candidate policies and split strategy. `COMPLETE`
- [x] **P0.5** Install the three design skills and confirm they appear in `npx skills list`. `COMPLETE`
- [x] **P0.6** Create `UI_DESIGN_RULES.md` and `UI_SPECIFICATION.md` from this plan. `COMPLETE`

## Phase 1 — CPU Simulator Foundation
- [x] **P1.1** Implement process/PCB data model and state transitions. `COMPLETE`
- [x] **P1.2** Implement deterministic event ordering and simulation clock. `COMPLETE`
- [x] **P1.3** Implement FCFS. `COMPLETE`
- [x] **P1.4** Implement SJF. `COMPLETE`
- [x] **P1.5** Implement Round Robin with configurable quantum. `COMPLETE`
- [x] **P1.6** Implement non-preemptive Priority. `COMPLETE`
- [x] **P1.7** Implement Gantt timeline generation. `COMPLETE`
- [x] **P1.8** Implement metric calculation and per-process metrics. `COMPLETE`
- [x] **P1.9** Add hand-calculated correctness fixtures and edge-case tests. `COMPLETE`

## Phase 2 — Workload Generation and Experiment Engine
- [x] **P2.1** Implement the five workload families. `COMPLETE`
- [x] **P2.2** Implement seed-controlled scenario generation and scenario export. `COMPLETE`
- [x] **P2.3** Implement pre-execution feature extraction and data dictionary. `COMPLETE`
- [x] **P2.4** Implement experiment matrix runner that replays identical scenarios against every policy. `COMPLETE`
- [x] **P2.5** Implement run IDs and immutable per-run artifact folders. `COMPLETE`
- [x] **P2.6** Implement JSON manifest, JSONL event trace, timeline CSV, process metrics CSV and aggregate JSON. `COMPLETE`
- [x] **P2.7** Implement experiment registry/index and failure status handling. `COMPLETE`
- [x] **P2.8** Run a pilot with 2–5 scenarios per workload family and inspect anomalies. `COMPLETE`

## Phase 3 — ML Recommender and Research Evaluation
- [x] **P3.1** Implement composite cost from frozen config weights. `COMPLETE`
- [x] **P3.2** Build scenario-level training table from baseline experiment outputs. `COMPLETE`
- [x] **P3.3** Implement scenario-grouped stratified 70/15/15 split. `COMPLETE`
- [x] **P3.4** Train bounded-depth Decision Tree and save model metadata. `COMPLETE`
- [x] **P3.5** Implement explanation/path output for predicted policy. `COMPLETE`
- [x] **P3.6** Implement fixed-policy baselines and per-scenario oracle comparison. `COMPLETE`
- [x] **P3.7** Implement held-out evaluation and regret metrics. `COMPLETE`
- [x] **P3.8** Measure model inference latency separately. `COMPLETE`
- [x] **P3.9** Run full CPU matrix (target 500 scenarios; document any reduction). `COMPLETE`
- [x] **P3.10** Generate summary tables, confidence intervals and workload-family analysis. `COMPLETE`
- [x] **P3.11** Run composite-score weight sensitivity analysis. `COMPLETE`

## Phase 4 — Linux I/O Experiment
- [x] **P4.1** Implement read-only host/device probe. `COMPLETE`
- [x] **P4.2** Detect exposed schedulers from sysfs; do not hardcode available options. `COMPLETE`
- [x] **P4.3** Implement scratch-directory and safe-file validation. `COMPLETE`
- [x] **P4.4** Generate `fio` job files for sequential read, random read, random write and mixed I/O. `COMPLETE`
- [x] **P4.5** Implement `fio` runner with JSON output, timeout and exit-status capture. `COMPLETE`
- [x] **P4.6** Implement parser for IOPS, bandwidth and latency percentiles. `COMPLETE`
- [x] **P4.7** Implement explicit/manual scheduler switching and restore workflow only if supported and authorised. `COMPLETE`
- [x] **P4.8** Test dry-run and safety guards; verify no raw-device target can be configured. `COMPLETE`
- [x] **P4.9** Run pilot, then final repetitions for all available scheduler/workload combinations. `COMPLETE`
- [x] **P4.10** Generate I/O comparison tables and host-specific limitations. `COMPLETE`

## Phase 5 — Dashboard
- [x] **P5.1** Implement page navigation and the visual design system. `COMPLETE`
- [x] **P5.2** Implement Overview with honest empty states and run status. `COMPLETE`
- [x] **P5.3** Implement CPU Lab controls, Gantt chart, metrics table and policy explanation. `COMPLETE`
- [x] **P5.4** Implement I/O Lab host status, safety confirmation, workload controls and results. `COMPLETE`
- [x] **P5.5** Implement Experiment Registry with filters and run-detail drilldown. `COMPLETE`
- [x] **P5.6** Implement Research Log and evidence links. `COMPLETE`
- [x] **P5.7** Implement Methodology & Reproducibility page. `COMPLETE`
- [x] **P5.8** Implement CSV/JSON export and reproducibility command display. `COMPLETE`
- [x] **P5.9** Run keyboard/accessibility/responsive checks. `COMPLETE`
- [x] **P5.10** Run frontend-design review, Vercel guidelines review and Impeccable critique/audit/polish; record issues and fixes. `COMPLETE`

## Phase 6 — Report, Demonstration and Release
- [x] **P6.1** Complete literature review with properly attributed papers and official documentation. `COMPLETE`
- [x] **P6.2** Complete architecture diagram and data-flow explanation. `COMPLETE`
- [x] **P6.3** Complete methodology, parameter, metric and reproducibility sections. `COMPLETE`
- [x] **P6.4** Complete results and discussion, including negative/neutral findings. `COMPLETE`
- [x] **P6.5** Complete limitations, threats to validity and future work. `COMPLETE`
- [x] **P6.6** Generate report figures/tables directly from saved results. `COMPLETE`
- [x] **P6.7** Verify conclusion-evidence matrix. `COMPLETE`
- [x] **P6.8** Prepare a short demo script and fallback screenshots exported from actual runs. `COMPLETE`
- [x] **P6.9** Run fresh-install reproduction test on another machine or clean environment if possible. `COMPLETE`
- [x] **P6.10** Tag final version and archive experiment manifests/results. `COMPLETE`
