"""
CLI script to execute safe Linux FIO benchmarking suite.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict
import yaml

from scheduling_lab.io_lab.fio_runner import FIORunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_fio_suite")


def load_config(config_path: str) -> Dict[str, Any]:
    p = Path(config_path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run safe Linux storage I/O benchmarks with fio.")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/io_defaults.yaml",
        help="Path to YAML I/O benchmark configuration",
    )
    parser.add_argument(
        "--confirm-scratch-file",
        action="store_true",
        help="Explicit confirmation that benchmark writes only to disposable scratch file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate parameters and output planned commands without running fio",
    )
    parser.add_argument(
        "--workload",
        type=str,
        default=None,
        choices=["seq_read", "rand_read", "rand_write", "mixed_randrw"],
        help="Specific workload to benchmark (default: all configured)",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=None,
        help="Override repetition count",
    )

    args = parser.parse_args()
    config = load_config(args.config)

    safety_cfg = config.get("safety", {})
    bench_cfg = config.get("benchmark", {})
    workloads = config.get("workloads", [])

    if safety_cfg.get("require_explicit_confirmation", True) and not args.confirm_scratch_file and not args.dry_run:
        logger.error(
            "SAFETY REQUIREMENT: You must pass --confirm-scratch-file to confirm that benchmarks "
            "will write exclusively to the designated disposable scratch file."
        )
        return 1

    runner = FIORunner(
        scratch_dir=safety_cfg.get("scratch_directory", "data/scratch"),
    )

    target_file = safety_cfg.get("target_file", "data/scratch/fio_test.dat")
    reps = args.repetitions or bench_cfg.get("repetitions", 3)
    runtime = bench_cfg.get("runtime_seconds", 10)
    rampup = bench_cfg.get("rampup_seconds", 2)
    file_size = bench_cfg.get("file_size_mib", 512)

    selected_workloads = [args.workload] if args.workload else [w["id"] for w in workloads]

    logger.info(f"Starting FIO Suite: {len(selected_workloads)} workloads x {reps} repetitions. Dry run: {args.dry_run}")

    for w_id in selected_workloads:
        for rep in range(1, reps + 1):
            logger.info(f"Running workload '{w_id}' (rep {rep}/{reps})...")
            res = runner.run_benchmark(
                workload_id=w_id,
                scheduler_name="current",
                repetition=rep,
                target_file=target_file,
                file_size_mib=file_size,
                runtime_seconds=runtime,
                rampup_seconds=rampup,
                dry_run=args.dry_run,
            )
            logger.info(f"Result {res.get('run_id')}: status={res.get('status')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
