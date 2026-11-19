"""
Unit tests for ML components: objective calculation, dataset splitting, explainability, and fallback.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from sklearn.tree import DecisionTreeClassifier

from scheduling_lab.ml.explain import explain_prediction
from scheduling_lab.ml.objective import compute_scenario_costs, find_winning_policy, normalize_component
from scheduling_lab.ml.recommender import PolicyRecommender
from scheduling_lab.ml.split import create_scenario_splits
from scheduling_lab.workloads.features import FEATURE_NAMES


def test_normalize_component_identical():
    res = normalize_component([10.0, 10.0, 10.0])
    assert res == [0.5, 0.5, 0.5]


def test_normalize_component_min_max():
    res = normalize_component([10.0, 20.0, 30.0], invert=False)
    assert pytest.approx(res) == [0.0, 0.5, 1.0]

    res_inv = normalize_component([10.0, 20.0, 30.0], invert=True)
    assert pytest.approx(res_inv) == [1.0, 0.5, 0.0]


def test_compute_scenario_costs():
    metrics = {
        "FCFS": {
            "avg_response_time": 10.0,
            "avg_waiting_time": 15.0,
            "avg_turnaround_time": 25.0,
            "context_switches": 2,
            "cpu_utilisation_pct": 95.0,
        },
        "RR_Q2": {
            "avg_response_time": 2.0,
            "avg_waiting_time": 8.0,
            "avg_turnaround_time": 20.0,
            "context_switches": 12,
            "cpu_utilisation_pct": 90.0,
        },
    }
    winner, win_cost, costs = find_winning_policy(metrics)
    assert winner in ["FCFS", "RR_Q2"]
    assert 0.0 <= win_cost <= 1.0
    assert "composite_cost" in costs["FCFS"]
    assert "composite_cost" in costs["RR_Q2"]


def test_scenario_grouped_split():
    # 20 scenarios, 4 families
    scenarios = [f"scen_{i}" for i in range(20)]
    families = ["cpu_bound", "io_bound", "interactive", "mixed"] * 5
    df = pd.DataFrame({"scenario_id": scenarios, "workload_family": families})

    splits = create_scenario_splits(df, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42)
    train_set = set(splits["train"])
    val_set = set(splits["validation"])
    test_set = set(splits["test"])

    # Disjointness check
    assert len(train_set.intersection(val_set)) == 0
    assert len(train_set.intersection(test_set)) == 0
    assert len(val_set.intersection(test_set)) == 0
    assert len(train_set) + len(val_set) + len(test_set) == 20


def test_explain_prediction():
    X = np.array([
        [10, 2.0, 1.0, 0.5, 5.0, 0.8, 0.3, 1.0, 0.5, 0.7, 1.2, 0.4],
        [10, 25.0, 5.0, 0.2, 0.5, 0.1, 10.0, 3.0, 1.0, 0.0, 1.5, 0.1],
    ])
    y = np.array(["RR_Q2", "FCFS"])
    clf = DecisionTreeClassifier(max_depth=2, random_state=42)
    clf.fit(X, y)

    sample_dict = {name: val for name, val in zip(FEATURE_NAMES, X[0])}
    explanation = explain_prediction(clf, FEATURE_NAMES, sample_dict)

    assert "predicted_policy" in explanation
    assert "decision_path" in explanation
    assert len(explanation["decision_path"]) > 0


def test_recommender_fallback():
    # Test with non-existent model path
    recommender = PolicyRecommender(model_path="non_existent.joblib", metadata_path="non_existent.json")
    assert not recommender.is_available

    from scheduling_lab.core.models import Process
    procs = [Process("P1", 0, 1, [5])]
    rec = recommender.recommend(procs)

    assert rec["is_fallback"] is True
    assert rec["recommended_policy"] == "RR_Q5"
    assert "Model unavailable" in rec["fallback_reason"]
