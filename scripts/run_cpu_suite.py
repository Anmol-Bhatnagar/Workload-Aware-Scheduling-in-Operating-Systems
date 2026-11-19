"""
CLI script to execute the CPU Scheduling Experiment Suite.
Supports both small pilots and full scenario matrices.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List
import yaml

from scheduling_lab.experiments.runner import DEFAULT_CANDIDATES, ExperimentRunner
from scheduling_lab.workloads.generator import WorkloadGenerator
from scheduling_lab.workloads.profiles import WorkloadFamily

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_cpu_suite")


def load_config(config_path: str) -> Dict[str, Any]:
    p = Path(config_path)
    if not p.exists():
        logger.warning(f"Config {config_path} not found. Using internal defaults.")
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CPU scheduling experiment matrix.")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/cpu_experiment_matrix.yaml",
        help="Path to YAML matrix configuration",
    )
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Run lightweight pilot (5 scenarios per family = 25 scenarios, 150 runs)",
    )
    parser.add_argument(
        "--scenarios-per-family",
        type=int,
        default=None,
        help="Override number of scenarios per workload family",
    )
    parser.add_argument(
        "--output-scenarios-dir",
        type=str,
        default="data/generated",
        help="Directory to save generated scenario definitions",
    )

    args = parser.parse_args()
    config = load_config(args.config)

    scenarios_dir = Path(args.output_scenarios_dir)
    scenarios_dir.mkdir(parents=True, exist_ok=True)

    matrix_cfg = config.get("matrix", {})
    scale_cfg = matrix_cfg.get("scale", {})
    base_seed = scale_cfg.get("base_seed", 2026)

    if args.scenarios_per_family is not None:
        count_per_fam = args.scenarios_per_family
    elif args.pilot:
        count_per_fam = scale_cfg.get("pilot_scenarios_per_family", 5)
    else:
        count_per_fam = scale_cfg.get("full_scenarios_per_family", 100)

    families = [
        WorkloadFamily.CPU_BOUND,
        WorkloadFamily.IO_BOUND,
        WorkloadFamily.INTERACTIVE,
        WorkloadFamily.MIXED,
        WorkloadFamily.BURSTY_ARRIVALS,
    ]

    logger.info(
        f"Generating and running CPU matrix: {len(families)} families x {count_per_fam} scenarios = "
        f"{len(families) * count_per_fam} scenarios total."
    )

    scenarios: List[Dict[str, Any]] = []
    scenario_idx = 0

    for fam in families:
        for i in range(count_per_fam):
            scenario_idx += 1
            seed = base_seed + scenario_idx
            scenario_id = f"{fam.value}_s{seed}_n10"
            scen_data = WorkloadGenerator.generate_scenario(
                family=fam,
                process_count=10,
                seed=seed,
                scenario_id=scenario_id,
            )
            # Save scenario file
            scen_file = scenarios_dir / f"{scenario_id}.json"
            with open(scen_file, "w", encoding="utf-8") as f:
                json.dump(scen_data, f, indent=2)

            scenarios.append(scen_data)

    runner = ExperimentRunner(candidates=DEFAULT_CANDIDATES)
    logger.info(f"Executing {len(scenarios) * len(DEFAULT_CANDIDATES)} policy evaluations...")
    results = runner.run_matrix(scenarios)

    completed = sum(1 for r in results if r["status"] == "COMPLETED")
    failed = sum(1 for r in results if r["status"] == "FAILED")

    logger.info(f"Execution complete: {completed} completed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
