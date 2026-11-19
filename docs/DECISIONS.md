# Architecture & Research Decisions Log

This document records key architectural, methodological, and research protocol decisions, their context, date, reason, and impact.

---

### DEC-001: Independent Local Discrete-Event CPU Simulator
- **Date:** 2026-11-19
- **Status:** Approved
- **Context:** Deciding between kernel-level modifications/eBPF vs user-space discrete-event simulation for CPU scheduling experiments.
- **Decision:** Build a single-threaded deterministic discrete-event CPU simulator in pure Python with exact event-ordering and state tracking.
- **Reason:** Kernel modification is inaccessible across diverse hardware, non-portable, and introduces uncontrolled background noise. A discrete-event simulator provides deterministic, exact reproducibility, enabling controlled ablation studies across CPU burst distributions and arrival dynamics.
- **Impact:** Core simulation logic is completely isolated from UI and OS-specific APIs; runnable headlessly in automated test suites and CLI matrix scripts.

---

### DEC-002: Separation of Educational Simulation from Real Linux I/O Benchmarking
- **Date:** 2026-11-19
- **Status:** Approved
- **Context:** Balancing theoretical CPU scheduling algorithms with real operating systems experiments.
- **Decision:** Split the study into two distinct components: a 75% effort discrete-event CPU scheduling study with an ML recommender, and a 25% effort empirical storage I/O benchmark using `fio` on Linux.
- **Reason:** Real kernel CPU schedulers (e.g. EEVDF) operate at microsecond scales with massive hardware interaction complexity, whereas storage block schedulers (`none`, `mq-deadline`, `bfq`, `kyber`) can be safely probed and benchmarked through standard sysfs interfaces and `fio` on disposable scratch files.
- **Impact:** Clear academic boundaries: no claims of modifying kernel CPU scheduling; safe, empirical I/O claims restricted to measured device capabilities.

---

### DEC-003: Interpretable Decision Tree Model for Policy Recommendation
- **Date:** 2026-11-19
- **Status:** Approved
- **Context:** Selecting the machine learning approach for policy selection based on pre-execution workload characteristics.
- **Decision:** Use a bounded-depth scikit-learn `DecisionTreeClassifier` (default depth <= 4).
- **Reason:** Scheduling policies require transparency and explainability. A decision tree provides human-readable decision paths (e.g. "if CPU/IO ratio < 0.3 then RR_Q2"), avoids black-box opacity, and has negligible inference latency (~microseconds) compared to neural networks.
- **Impact:** High interpretability for research presentation; clear feature attribution; straightforward verification against textbook scheduling intuition.

---

### DEC-004: Strict Scenario-Grouped Train/Validation/Test Split
- **Date:** 2026-11-19
- **Status:** Approved
- **Context:** Preventing data leakage between identical workload scenarios evaluated across multiple scheduling policies.
- **Decision:** All policy evaluations for a given generated workload scenario share the same scenario ID and are partitioned together into 70% train, 15% validation, and 15% test splits.
- **Reason:** A single scenario yields 6 candidate policy runs. Splitting on individual rows would result in severe data leakage where the test set contains known scenarios evaluated under different policies.
- **Impact:** Clean, held-out generalization testing; robust evaluation against fixed baselines.

---

### DEC-005: Strict I/O Safety Protocol
- **Date:** 2026-11-19
- **Status:** Approved
- **Context:** Protecting host storage devices from accidental corruption during I/O scheduler benchmarking.
- **Decision:** Prohibit any raw block-device targeting (`/dev/sd*`, `/dev/nvme*`). Mandate file-backed `fio` benchmarks targeting disposable files inside a designated scratch directory.
- **Reason:** Raw writes risk wiping partitions or operating system files. Disposable file testing provides accurate relative comparisons across schedulers without data loss risks.
- **Impact:** Safe execution on standard workstations and Linux test environments.
