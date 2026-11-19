"""
Unit tests for workload generator and profile characteristics.
"""

from scheduling_lab.workloads.generator import WorkloadGenerator
from scheduling_lab.workloads.profiles import WorkloadFamily


def test_workload_generation_all_families():
    families = [
        WorkloadFamily.CPU_BOUND,
        WorkloadFamily.IO_BOUND,
        WorkloadFamily.INTERACTIVE,
        WorkloadFamily.MIXED,
        WorkloadFamily.BURSTY_ARRIVALS,
    ]
    for fam in families:
        scen = WorkloadGenerator.generate_scenario(family=fam, process_count=8, seed=123)
        assert scen["workload_family"] == fam.value
        assert scen["process_count"] == 8
        assert len(scen["processes"]) == 8
        # Validate process structure
        for p in scen["processes"]:
            assert p["arrival_time"] >= 0
            assert 1 <= p["priority"] <= 5
            assert len(p["cpu_bursts"]) >= 1
            assert all(b > 0 for b in p["cpu_bursts"])
            assert all(b >= 0 for b in p.get("io_bursts", []))


def test_workload_generation_determinism():
    scen1 = WorkloadGenerator.generate_scenario(family="cpu_bound", process_count=10, seed=999)
    scen2 = WorkloadGenerator.generate_scenario(family="cpu_bound", process_count=10, seed=999)
    assert scen1 == scen2


def test_workload_reloading():
    scen = WorkloadGenerator.generate_scenario(family="interactive", process_count=5, seed=42)
    processes = WorkloadGenerator.load_scenario_processes(scen)
    assert len(processes) == 5
    assert processes[0].pid == "P1"
