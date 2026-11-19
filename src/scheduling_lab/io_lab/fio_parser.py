"""
FIO JSON output parser.
Extracts throughput (MiB/s), IOPS, and latency distributions (Mean, p95, p99).
"""

from __future__ import annotations

import json
from typing import Any, Dict


def parse_fio_json(fio_data: Dict[str, Any] | str) -> Dict[str, Any]:
    """Parse raw fio JSON object into normalized performance metrics."""
    if isinstance(fio_data, str):
        data = json.loads(fio_data)
    else:
        data = fio_data

    jobs = data.get("jobs", [])
    if not jobs:
        raise ValueError("Invalid fio output: no job entries found")

    job = jobs[0]
    read_stat = job.get("read", {})
    write_stat = job.get("write", {})

    # Bandwidth in KiB/s -> convert to MiB/s
    read_bw_kib = float(read_stat.get("bw", 0))
    write_bw_kib = float(write_stat.get("bw", 0))
    total_bw_mib = (read_bw_kib + write_bw_kib) / 1024.0

    read_iops = float(read_stat.get("iops", 0))
    write_iops = float(write_stat.get("iops", 0))
    total_iops = read_iops + write_iops

    # Latencies in nanoseconds or microseconds depending on fio version; fio reports clat_ns
    read_clat = read_stat.get("clat_ns", {})
    write_clat = write_stat.get("clat_ns", {})

    read_mean_lat_us = float(read_clat.get("mean", 0)) / 1000.0
    write_mean_lat_us = float(write_clat.get("mean", 0)) / 1000.0

    # Percentiles
    read_p95_us = float(read_clat.get("percentile", {}).get("95.000000", 0)) / 1000.0
    read_p99_us = float(read_clat.get("percentile", {}).get("99.000000", 0)) / 1000.0

    write_p95_us = float(write_clat.get("percentile", {}).get("95.000000", 0)) / 1000.0
    write_p99_us = float(write_clat.get("percentile", {}).get("99.000000", 0)) / 1000.0

    # Combined representative latency
    overall_mean_lat_us = max(read_mean_lat_us, write_mean_lat_us)
    overall_p95_us = max(read_p95_us, write_p95_us)
    overall_p99_us = max(read_p99_us, write_p99_us)

    return {
        "job_name": job.get("jobname", "unknown"),
        "error_code": job.get("error", 0),
        "bandwidth_mib_s": {
            "read": round(read_bw_kib / 1024.0, 3),
            "write": round(write_bw_kib / 1024.0, 3),
            "total": round(total_bw_mib, 3),
        },
        "iops": {
            "read": round(read_iops, 2),
            "write": round(write_iops, 2),
            "total": round(total_iops, 2),
        },
        "latency_us": {
            "mean": round(overall_mean_lat_us, 2),
            "p95": round(overall_p95_us, 2),
            "p99": round(overall_p99_us, 2),
        },
        "runtime_ms": job.get("elapsed", 0) * 1000,
    }
