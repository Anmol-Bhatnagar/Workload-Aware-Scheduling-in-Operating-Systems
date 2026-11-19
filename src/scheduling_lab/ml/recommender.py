"""
High-level policy recommender service with explainability and safe fallback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib

from scheduling_lab.core.models import Process
from scheduling_lab.ml.explain import explain_prediction
from scheduling_lab.workloads.features import FEATURE_NAMES, PreExecutionFeatureExtractor


class PolicyRecommender:
    """Provides inference, explainability, and fallback safety for scheduling recommendations."""

    def __init__(
        self,
        model_path: Path | str = "models/decision_tree_recommender.joblib",
        metadata_path: Path | str = "models/model_metadata.json",
        fallback_policy: str = "RR_Q5",
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.fallback_policy = fallback_policy

        self.model: Optional[Any] = None
        self.metadata: Optional[Dict[str, Any]] = None
        self._load()

    def _load(self) -> None:
        if self.model_path.exists() and self.metadata_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception:
                self.model = None
                self.metadata = None

    @property
    def is_available(self) -> bool:
        return self.model is not None and self.metadata is not None

    def recommend(self, processes: List[Process]) -> Dict[str, Any]:
        """Recommend a scheduling policy for a set of processes."""
        features = PreExecutionFeatureExtractor.extract_features(processes)

        if not self.is_available:
            return {
                "recommended_policy": self.fallback_policy,
                "is_fallback": True,
                "fallback_reason": "Model unavailable — using selected fixed baseline",
                "features": features,
                "explanation": None,
            }

        explanation = explain_prediction(
            tree=self.model,
            feature_names=FEATURE_NAMES,
            sample_features=features,
        )

        return {
            "recommended_policy": explanation["predicted_policy"],
            "is_fallback": False,
            "fallback_reason": None,
            "features": features,
            "explanation": explanation,
        }
