"""
CLI script to probe Linux host hardware, block devices, and I/O schedulers.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from scheduling_lab.io_lab.host_probe import probe_host

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_io_probe")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe host OS and storage I/O capabilities.")
    parser.add_argument(
        "--output",
        type=str,
        default="results/host_probe.json",
        help="Path to save output JSON host probe report",
    )
    parser.add_argument(
        "--scratch-dir",
        type=str,
        default="data/scratch",
        help="Directory to check storage metrics for",
    )
    args = parser.parse_args()

    logger.info("Executing read-only host discovery probe...")
    report = probe_host(target_dir=args.scratch_dir)

    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Host probe saved to {out_p}")
    logger.info(f"OS: {report['os']['platform']}")
    logger.info(f"Environment: {report['virtualization']['environment_type']}")
    logger.info(f"FIO Installed: {report['tools']['fio_installed']} ({report['tools']['fio_version']})")
    logger.info(f"Block devices discovered: {len(report['storage']['block_devices'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
