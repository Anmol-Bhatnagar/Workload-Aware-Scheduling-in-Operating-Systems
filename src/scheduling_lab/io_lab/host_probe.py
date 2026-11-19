"""
Linux Host Hardware & Environment Discovery Probe.
Read-only inspection of system metadata, CPU, memory, block devices, and exposed I/O schedulers.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import psutil


def get_fio_version() -> Optional[str]:
    """Check if fio executable is available and return version string."""
    fio_bin = shutil.which("fio")
    if not fio_bin:
        return None
    try:
        proc = subprocess.run([fio_bin, "--version"], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return None


def probe_block_devices() -> List[Dict[str, Any]]:
    """Discover block devices and their available I/O schedulers from sysfs."""
    devices: List[Dict[str, Any]] = []
    sys_block = Path("/sys/block")
    if not sys_block.exists() or not sys_block.is_dir():
        return devices

    for dev_path in sys_block.iterdir():
        dev_name = dev_path.name
        # Skip loop and ram devices
        if dev_name.startswith(("loop", "ram")):
            continue

        sched_file = dev_path / "queue" / "scheduler"
        schedulers: List[str] = []
        current_sched: Optional[str] = None
        is_writable = False

        if sched_file.exists():
            try:
                is_writable = os.access(sched_file, os.W_OK)
                with open(sched_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                # Content format: "none [mq-deadline] kyber bfq"
                for item in content.split():
                    if item.startswith("[") and item.endswith("]"):
                        clean_item = item[1:-1]
                        current_sched = clean_item
                        schedulers.append(clean_item)
                    else:
                        schedulers.append(item)
            except Exception:
                pass

        devices.append({
            "name": dev_name,
            "path": f"/dev/{dev_name}",
            "available_schedulers": schedulers,
            "current_scheduler": current_sched,
            "scheduler_writable": is_writable,
        })

    return devices


def detect_virtualization() -> Dict[str, Any]:
    """Detect if running inside WSL, container, or VM."""
    is_wsl = False
    is_docker = False
    details = "Native OS"

    if platform.system().lower() == "linux":
        try:
            with open("/proc/version", "r", encoding="utf-8") as f:
                ver_text = f.read().lower()
                if "microsoft" in ver_text or "wsl" in ver_text:
                    is_wsl = True
                    details = "WSL (Windows Subsystem for Linux)"
        except Exception:
            pass

        if Path("/.dockerenv").exists():
            is_docker = True
            details = "Docker Container"
    elif platform.system().lower() == "windows":
        details = "Microsoft Windows Host"

    return {
        "is_wsl": is_wsl,
        "is_container": is_docker,
        "environment_type": details,
    }


def probe_host(target_dir: Path | str = "data/scratch") -> Dict[str, Any]:
    """Execute complete read-only host discovery."""
    target_path = Path(target_dir).resolve()
    ram = psutil.virtual_memory()

    # Disk partition / mount information for target_dir
    disk_info: Dict[str, Any] = {}
    try:
        usage = psutil.disk_usage(str(target_path if target_path.exists() else target_path.parent))
        disk_info["total_gib"] = round(usage.total / (1024**3), 2)
        disk_info["free_gib"] = round(usage.free / (1024**3), 2)
        disk_info["used_pct"] = round(usage.percent, 1)
    except Exception:
        pass

    block_devices = probe_block_devices()
    virt = detect_virtualization()

    report = {
        "timestamp": platform.node(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "cpu": {
            "model": platform.processor(),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
        },
        "memory": {
            "total_gib": round(ram.total / (1024**3), 2),
            "available_gib": round(ram.available / (1024**3), 2),
        },
        "storage": {
            "target_scratch_dir": str(target_path),
            "target_disk_usage": disk_info,
            "block_devices": block_devices,
        },
        "tools": {
            "fio_version": get_fio_version(),
            "fio_installed": get_fio_version() is not None,
        },
        "virtualization": virt,
    }
    return report
