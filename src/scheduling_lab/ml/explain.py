"""
Explainability module for the Decision Tree policy recommender.
Converts tree node traversals into transparent human-readable rule paths.
"""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
from sklearn.tree import DecisionTreeClassifier


def explain_prediction(
    tree: DecisionTreeClassifier,
    feature_names: List[str],
    sample_features: Dict[str, float],
) -> Dict[str, Any]:
    """Generate a step-by-step interpretable decision path for a single workload scenario."""
    x_vec = np.array([[sample_features[name] for name in feature_names]], dtype=float)
    node_indicator = tree.decision_path(x_vec)
    leaf_id = tree.apply(x_vec)[0]
    predicted_idx = np.argmax(tree.predict_proba(x_vec)[0])
    predicted_class = tree.classes_[predicted_idx]
    confidence = float(tree.predict_proba(x_vec)[0][predicted_idx])

    feature = tree.tree_.feature
    threshold = tree.tree_.threshold

    node_index = node_indicator.indices[node_indicator.indptr[0] : node_indicator.indptr[1]]
    rules: List[Dict[str, Any]] = []

    for node_id in node_index:
        if leaf_id == node_id:
            continue

        feat_idx = feature[node_id]
        feat_name = feature_names[feat_idx]
        val = sample_features[feat_name]
        thresh = threshold[node_id]

        if val <= thresh:
            direction = "<="
            comparison = f"{feat_name} ({val:.3f}) <= {thresh:.3f}"
        else:
            direction = ">"
            comparison = f"{feat_name} ({val:.3f}) > {thresh:.3f}"

        rules.append({
            "node_id": int(node_id),
            "feature": feat_name,
            "value": round(val, 4),
            "threshold": round(float(thresh), 4),
            "direction": direction,
            "rule_text": comparison,
        })

    return {
        "predicted_policy": str(predicted_class),
        "confidence": round(confidence, 4),
        "class_probabilities": {
            str(cls_name): round(float(prob), 4)
            for cls_name, prob in zip(tree.classes_, tree.predict_proba(x_vec)[0])
        },
        "decision_path": rules,
        "leaf_id": int(leaf_id),
    }
