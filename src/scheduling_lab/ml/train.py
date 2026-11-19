"""
Model training pipeline for Decision Tree CPU policy recommendation.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from scheduling_lab.workloads.features import FEATURE_NAMES


class ModelTrainer:
    """Trains, validates, and serializes the explainable Decision Tree policy recommender."""

    def __init__(
        self,
        max_depth: int = 4,
        min_samples_leaf: int = 5,
        random_state: int = 42,
        models_dir: Path | str = "models",
    ) -> None:
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        df: pd.DataFrame,
        train_scenario_ids: List[str],
        val_scenario_ids: Optional[List[str]] = None,
    ) -> Tuple[DecisionTreeClassifier, Dict[str, Any]]:
        train_df = df[df["scenario_id"].isin(train_scenario_ids)]
        if train_df.empty:
            raise ValueError("Training dataset is empty for given scenario IDs")

        X_train = train_df[FEATURE_NAMES].values
        y_train = train_df["target_policy"].values

        clf = DecisionTreeClassifier(
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            random_state=self.random_state,
            criterion="gini",
        )
        clf.fit(X_train, y_train)

        train_acc = float(clf.score(X_train, y_train))
        val_acc: Optional[float] = None

        if val_scenario_ids:
            val_df = df[df["scenario_id"].isin(val_scenario_ids)]
            if not val_df.empty:
                X_val = val_df[FEATURE_NAMES].values
                y_val = val_df["target_policy"].values
                val_acc = float(clf.score(X_val, y_val))

        # Measure inference latency over 1000 repetitions
        sample_x = X_train[0:1]
        latencies_ns: List[int] = []
        for _ in range(1000):
            t0 = time.perf_counter_ns()
            _ = clf.predict(sample_x)
            t1 = time.perf_counter_ns()
            latencies_ns.append(t1 - t0)

        median_latency_us = float(np.median(latencies_ns)) / 1000.0
        p95_latency_us = float(np.percentile(latencies_ns, 95)) / 1000.0

        metadata = {
            "model_type": "DecisionTreeClassifier",
            "max_depth": self.max_depth,
            "min_samples_leaf": self.min_samples_leaf,
            "random_state": self.random_state,
            "feature_names": FEATURE_NAMES,
            "classes": [str(c) for c in clf.classes_],
            "train_sample_count": len(train_df),
            "train_accuracy": round(train_acc, 4),
            "val_accuracy": round(val_acc, 4) if val_acc is not None else None,
            "inference_latency_us": {
                "median": round(median_latency_us, 3),
                "p95": round(p95_latency_us, 3),
            },
            "timestamp": time.time(),
        }

        # Save artifacts
        model_path = self.models_dir / "decision_tree_recommender.joblib"
        meta_path = self.models_dir / "model_metadata.json"

        joblib.dump(clf, model_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return clf, metadata
