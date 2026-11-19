"""
Safe FIO execution runner.
Enforces safety validations, dry-run previews, timeout guards, and raw result archiving.
"""

from __future__ import annotations

import json
import logging
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from scheduling_lab.experiments.registry import ExperimentRegistry
from scheduling_lab.io_lab.fio_jobs import generate_fio_job_content, validate_safe_target_path
from scheduling_lab.io_lab.fio_parser import parse_fio_json
from scheduling_lab.io_lab.host_probe import probe_host

logger = logging.getLogger(__name__)


class FIORunner:
    """Executes safe, file-backed fio benchmarks on Linux."""

    def __init__(
        self,
        runs_dir: Path | str = "results/runs",
        scratch_dir: Path | str = "data/scratch",
        registry: Optional[ExperimentRegistry] = None,
    ) -> None:
        self.runs_dir = Path(runs_dir)
        self.scratch_dir = Path(scratch_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry or ExperimentRegistry(registry_path=self.runs_dir / "registry.json")

    def run_benchmark(
        self,
        workload_id: str,
        scheduler_name: str = "current",
        repetition: int = 1,
        target_file: Optional[Path | str] = None,
        file_size_mib: int = 512,
        runtime_seconds: int = 10,
        rampup_seconds: int = 2,
        direct_io: int = 1,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Run a single benchmark repetition with complete artifact capture."""
        target_path = target_file or (self.scratch_dir / "fio_test.dat")
        safe_target = validate_safe_target_path(target_path, self.scratch_dir)

        run_id = f"io_{workload_id}_{scheduler_name}_rep{repetition}"
        run_folder = self.runs_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        job_content = generate_fio_job_content(
            workload_id=workload_id,
            target_file=safe_target,
            file_size_mib=file_size_mib,
            runtime_seconds=runtime_seconds,
            rampup_seconds=rampup_seconds,
            direct_io=direct_io,
            io_engine="libaio" if platform.system().lower() == "linux" else "sync",
        )

        job_file = run_folder / "fio_job.fio"
        with open(job_file, "w", encoding="utf-8") as f:
            f.write(job_content)

        host_info = probe_host(self.scratch_dir)
        with open(run_folder / "host_probe.json", "w", encoding="utf-8") as f:
            json.dump(host_info, f, indent=2)

        if dry_run:
            logger.info(f"[DRY-RUN] Benchmark {run_id} validated. Target file: {safe_target}")
            return {
                "run_id": run_id,
                "status": "DRY_RUN",
                "target_file": str(safe_target),
                "job_file": str(job_file),
            }

        fio_bin = shutil.which("fio")
        if not fio_bin:
            err_msg = (
                "fio executable not found on host. "
                "Linux fio benchmarking requires fio package installed (e.g. apt install fio)."
            )
            logger.warning(err_msg)
            entry = self.registry.register_run(
                run_id=run_id,
                experiment_type="IO",
                scenario_id=f"io_{workload_id}",
                policy=scheduler_name,
                workload_family=workload_id,
                status="UNAVAILABLE",
                error_message=err_msg,
            )
            return entry

        # Execute fio command
        cmd = [fio_bin, "--output-format=json", str(job_file)]
        start_time = time.time()

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=runtime_seconds + rampup_seconds + 30,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode

            with open(run_folder / "fio_stdout.log", "w", encoding="utf-8") as f:
                f.write(stdout)
            with open(run_folder / "fio_stderr.log", "w", encoding="utf-8") as f:
                f.write(stderr)

            if exit_code != 0:
                raise RuntimeError(f"fio exited with non-zero code {exit_code}: {stderr[:300]}")

            raw_json = json.loads(stdout)
            with open(run_folder / "fio_output.json", "w", encoding="utf-8") as f:
                json.dump(raw_json, f, indent=2)

            parsed = parse_fio_json(raw_json)
            with open(run_folder / "parsed_metrics.json", "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)

            manifest = {
                "run_id": run_id,
                "workload_id": workload_id,
                "scheduler": scheduler_name,
                "repetition": repetition,
                "target_file": str(safe_target),
                "file_size_mib": file_size_mib,
                "status": "COMPLETED",
                "duration_seconds": round(time.time() - start_time, 2),
            }
            with open(run_folder / "run_manifest.json", "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            entry = self.registry.register_run(
                run_id=run_id,
                experiment_type="IO",
                scenario_id=f"io_{workload_id}",
                policy=scheduler_name,
                workload_family=workload_id,
                status="COMPLETED",
                summary_metrics=parsed,
            )
            return entry

        except Exception as exc:
            logger.error(f"FIO run failed: {exc}")
            manifest = {
                "run_id": run_id,
                "workload_id": workload_id,
                "scheduler": scheduler_name,
                "repetition": repetition,
                "target_file": str(safe_target),
                "status": "FAILED",
                "error": str(exc),
            }
            with open(run_folder / "run_manifest.json", "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            entry = self.registry.register_run(
                run_id=run_id,
                experiment_type="IO",
                scenario_id=f"io_{workload_id}",
                policy=scheduler_name,
                workload_family=workload_id,
                status="FAILED",
                error_message=str(exc),
            )
            return entry
