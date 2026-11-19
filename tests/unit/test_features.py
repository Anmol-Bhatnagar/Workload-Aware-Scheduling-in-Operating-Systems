"""
Unit tests for pre-execution feature extraction and leakage prevention.
"""

from scheduling_lab.workloads.features import FEATURE_NAMES, PreExecutionFeatureExtractor
from scheduling_lab.workloads.generator import WorkloadGenerator


def test_feature_extraction_completeness():
    scen = WorkloadGenerator.generate_scenario(family="mixed", process_count=10, seed=42)
    processes = WorkloadGenerator.load_scenario_processes(scen)

    features = PreExecutionFeatureExtractor.extract_features(processes)
    assert len(features) == len(FEATURE_NAMES)
    for name in FEATURE_NAMES:
        assert name in features
        assert isinstance(features[name], (int, float))

    vec = PreExecutionFeatureExtractor.extract_vector(processes)
    assert len(vec) == 12


def test_leakage_absence():
    """Ensure no post-execution keys exist in pre-execution features."""
    forbidden = ["turnaround", "waiting", "response", "context_switch", "makespan", "completion"]
    scen = WorkloadGenerator.generate_scenario(family="cpu_bound", process_count=10, seed=42)
    processes = WorkloadGenerator.load_scenario_processes(scen)
    features = PreExecutionFeatureExtractor.extract_features(processes)

    for k in features.keys():
        for f in forbidden:
            assert f not in k.lower(), f"Potential leakage detected in feature key: {k}"
