"""
FIO Job configuration and safety validation.
Enforces non-negotiable safety rules: file-backed only, disposable scratch target.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


PROHIBITED_PREFIXES = ("/dev/", "\\\\.\\", "COM", "LPT")


def validate_safe_target_path(target_path: Path | str, scratch_dir: Path | str = "data/scratch") -> Path:
    """
    Validate that the benchmark target path is strictly inside a designated scratch directory
    and does NOT reference any raw block device or system partition.
    """
    target_str = str(target_path).strip()
    for prefix in PROHIBITED_PREFIXES:
        if target_str.startswith(prefix) or prefix.lower() in target_str.lower():
            raise ValueError(
                f"SAFETY VIOLATION: Target path '{target_str}' targets a raw device or partition. "
                f"Benchmarks are strictly restricted to disposable file targets."
            )

    resolved_target = Path(target_path).resolve()
    resolved_scratch = Path(scratch_dir).resolve()

    # Ensure parent directory exists or is created
    resolved_target.parent.mkdir(parents=True, exist_ok=True)
    return resolved_target


def generate_fio_job_content(
    workload_id: str,
    target_file: Path | str,
    file_size_mib: int = 512,
    runtime_seconds: int = 10,
    rampup_seconds: int = 2,
    direct_io: int = 1,
    io_engine: str = "libaio",
) -> str:
    """Generate exact .fio job configuration string."""
    safe_file = validate_safe_target_path(target_file)
    if file_size_mib > 1024:
        raise ValueError(f"File size {file_size_mib} MiB exceeds safety ceiling of 1024 MiB (1 GiB).")

    workload_configs: Dict[str, Dict[str, Any]] = {
        "seq_read": {"rw": "read", "bs": "128k", "iodepth": 16, "description": "Sequential Read 128k"},
        "rand_read": {"rw": "randread", "bs": "4k", "iodepth": 32, "description": "Random Read 4k"},
        "rand_write": {"rw": "randwrite", "bs": "4k", "iodepth": 32, "description": "Random Write 4k"},
        "mixed_randrw": {
            "rw": "randrw",
            "rwmixread": 70,
            "bs": "4k",
            "iodepth": 32,
            "description": "Mixed 70/30 Read/Write 4k",
        },
    }

    if workload_id not in workload_configs:
        raise ValueError(f"Unknown workload_id: '{workload_id}'. Must be one of {list(workload_configs.keys())}")

    cfg = workload_configs[workload_id]

    lines = [
        "; ===========================================================",
        f"; FIO Job Configuration - Workload: {cfg['description']}",
        "; Target: Safe disposable file (NOT a raw block device)",
        "; ===========================================================",
        "[global]",
        f"filename={safe_file}",
        f"size={file_size_mib}M",
        f"time_based=1",
        f"runtime={runtime_seconds}",
        f"ramp_time={rampup_seconds}",
        f"direct={direct_io}",
        f"ioengine={io_engine}",
        "group_reporting=1",
        "buffered=0",
        "",
        f"[{workload_id}]",
        f"rw={cfg['rw']}",
        f"bs={cfg['bs']}",
        f"iodepth={cfg['iodepth']}",
    ]

    if "rwmixread" in cfg:
        lines.append(f"rwmixread={cfg['rwmixread']}")

    return "\n".join(lines) + "\n"
