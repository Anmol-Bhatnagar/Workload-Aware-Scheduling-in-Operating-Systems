"""
Unit tests for Linux I/O benchmarking components, safety validation, job generation, and JSON parser.
"""

from pathlib import Path
import pytest

from scheduling_lab.io_lab.fio_jobs import generate_fio_job_content, validate_safe_target_path
from scheduling_lab.io_lab.fio_parser import parse_fio_json
from scheduling_lab.io_lab.fio_runner import FIORunner


def test_safety_validation_prohibits_raw_devices():
    prohibited = [
        "/dev/sda",
        "/dev/nvme0n1",
        "/dev/sda1",
        "\\\\.\\PhysicalDrive0",
    ]
    for target in prohibited:
        with pytest.raises(ValueError, match="SAFETY VIOLATION"):
            validate_safe_target_path(target, scratch_dir="data/scratch")


def test_safety_validation_accepts_scratch_file():
    safe_path = "data/scratch/disposable_test.dat"
    resolved = validate_safe_target_path(safe_path, scratch_dir="data/scratch")
    assert resolved.name == "disposable_test.dat"


def test_fio_job_generation():
    content = generate_fio_job_content(
        workload_id="seq_read",
        target_file="data/scratch/test.dat",
        file_size_mib=256,
        runtime_seconds=5,
    )
    assert "[seq_read]" in content
    assert "rw=read" in content
    assert "bs=128k" in content
    assert "size=256M" in content


def test_fio_job_generation_size_limit():
    with pytest.raises(ValueError, match="exceeds safety ceiling"):
        generate_fio_job_content(
            workload_id="seq_read",
            target_file="data/scratch/test.dat",
            file_size_mib=2048,
        )


def test_fio_json_parser():
    mock_fio_output = {
        "jobs": [
            {
                "jobname": "seq_read",
                "error": 0,
                "elapsed": 10,
                "read": {
                    "bw": 1048576,  # 1024 MiB/s in KiB/s
                    "iops": 8192.0,
                    "clat_ns": {
                        "mean": 120000.0,  # 120 µs
                        "percentile": {
                            "95.000000": 250000,  # 250 µs
                            "99.000000": 450000,  # 450 µs
                        },
                    },
                },
                "write": {
                    "bw": 0,
                    "iops": 0,
                    "clat_ns": {"mean": 0, "percentile": {}},
                },
            }
        ]
    }
    metrics = parse_fio_json(mock_fio_output)
    assert metrics["bandwidth_mib_s"]["total"] == 1024.0
    assert metrics["iops"]["total"] == 8192.0
    assert metrics["latency_us"]["mean"] == 120.0
    assert metrics["latency_us"]["p95"] == 250.0
    assert metrics["latency_us"]["p99"] == 450.0


def test_fio_runner_dry_run():
    runner = FIORunner(runs_dir="results/runs", scratch_dir="data/scratch")
    res = runner.run_benchmark(
        workload_id="rand_read",
        scheduler_name="none",
        repetition=1,
        dry_run=True,
    )
    assert res["status"] == "DRY_RUN"
    assert "fio_test.dat" in res["target_file"]
