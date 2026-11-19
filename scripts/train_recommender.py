"""
CLI script to build dataset, train Decision Tree recommender, and evaluate on held-out split.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict
import joblib
import yaml

from scheduling_lab.ml.dataset import DatasetBuilder
from scheduling_lab.ml.evaluate import Evaluator
from scheduling_lab.ml.objective import DEFAULT_WEIGHTS
from scheduling_lab.ml.split import create_scenario_splits, load_scenario_splits
from scheduling_lab.ml.train import ModelTrainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_recommender")


def load_config(config_path: str) -> Dict[str, Any]:
    p = Path(config_path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and evaluate ML policy recommender.")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/ml_config.yaml",
        help="Path to YAML configuration",
    )
    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="Skip training and run evaluation on saved model",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["train", "validation", "test"],
        help="Dataset split to evaluate",
    )
    parser.add_argument(
        "--run-sensitivity",
        action="store_true",
        help="Run sensitivity analysis comparing primary vs alternative composite score weights",
    )
    args = parser.parse_args()
    config = load_config(args.config)

    weights = config.get("objective_weights", {}).get("primary", DEFAULT_WEIGHTS)
    model_cfg = config.get("model", {})
    max_depth = model_cfg.get("max_depth", 4)
    min_samples_leaf = model_cfg.get("min_samples_leaf", 5)
    random_state = model_cfg.get("random_state", 42)

    logger.info("Building scenario dataset from experiment runs...")
    builder = DatasetBuilder()
    df = builder.build_dataset(weights=weights)

    if df.empty:
        logger.error("No complete scenario runs found in results/runs. Run CPU experiments first.")
        return 1

    logger.info(f"Loaded dataset with {len(df)} scenarios across {df['workload_family'].nunique()} families.")

    splits_file = Path("data/splits.json")
    should_create = True
    if splits_file.exists():
        try:
            splits = load_scenario_splits(splits_file)
            if set(splits.get("train", [])).issubset(set(df["scenario_id"])):
                should_create = False
                logger.info("Loaded valid scenario splits from data/splits.json.")
            else:
                logger.info("Existing splits do not match dataset scenarios. Re-partitioning...")
        except Exception:
            should_create = True

    if should_create:
        logger.info("Creating 70/15/15 scenario-grouped stratified splits...")
        splits = create_scenario_splits(df, random_state=random_state, save_path=splits_file)

    train_scenarios = splits["train"]
    val_scenarios = splits["validation"]
    test_scenarios = splits["test"]

    # Determine Best Fixed Policy using train + val scenarios only!
    train_val_scenarios = train_scenarios + val_scenarios
    best_fixed, best_fixed_cost = Evaluator.find_best_fixed_policy(df, train_val_scenarios)
    logger.info(f"Best fixed policy on train/val: {best_fixed} (avg cost: {best_fixed_cost:.4f})")

    model_path = Path("models/decision_tree_recommender.joblib")

    if not args.evaluate_only:
        logger.info(f"Training DecisionTreeClassifier (max_depth={max_depth})...")
        trainer = ModelTrainer(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
        )
        model, metadata = trainer.train(df, train_scenarios, val_scenarios)
        logger.info(
            f"Trained model. Train Acc: {metadata['train_accuracy']:.4f}, "
            f"Val Acc: {metadata.get('val_accuracy')}, "
            f"Median latency: {metadata['inference_latency_us']['median']:.2f} µs"
        )
    else:
        if not model_path.exists():
            logger.error(f"Cannot run --evaluate-only: model not found at {model_path}")
            return 1
        model = joblib.load(model_path)

    # Held-out evaluation
    eval_scenarios = test_scenarios if args.split == "test" else (val_scenarios if args.split == "validation" else train_scenarios)
    logger.info(f"Evaluating model on {args.split} split ({len(eval_scenarios)} scenarios)...")
    eval_results = Evaluator.evaluate(
        model=model,
        df=df,
        test_scenario_ids=eval_scenarios,
        best_fixed_policy=best_fixed,
    )

    results_dir = Path("results/tables")
    results_dir.mkdir(parents=True, exist_ok=True)
    out_file = results_dir / f"ml_evaluation_{args.split}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    logger.info(f"Saved evaluation results to {out_file}")
    logger.info(f"Test Accuracy: {eval_results['policy_accuracy']:.4f}")
    logger.info("Average Composite Costs:")
    for k, v in eval_results["average_composite_costs"].items():
        logger.info(f"  - {k}: {v:.4f}")
    logger.info(f"ML beats RR_Q5 in: {eval_results['head_to_head_ratios']['ml_beats_rr5'] * 100:.1f}% of scenarios")
    logger.info(f"Bootstrap 95% CI (RR5 - ML): [{eval_results['bootstrap_ci_rr5_minus_ml_cost']['ci_2_5']:.4f}, {eval_results['bootstrap_ci_rr5_minus_ml_cost']['ci_97_5']:.4f}]")

    if args.run_sensitivity:
        sens_weights = config.get("objective_weights", {}).get("alternative_sensitivity")
        if sens_weights:
            logger.info("Running sensitivity analysis under alternative objective weights...")
            sens_df = builder.build_dataset(weights=sens_weights)
            sens_eval = Evaluator.evaluate(
                model=model,
                df=sens_df,
                test_scenario_ids=eval_scenarios,
                best_fixed_policy=best_fixed,
            )
            sens_out_file = results_dir / "sensitivity_analysis.json"
            with open(sens_out_file, "w", encoding="utf-8") as f:
                json.dump({
                    "primary_weights": weights,
                    "primary_results": eval_results["average_composite_costs"],
                    "alternative_weights": sens_weights,
                    "alternative_results": sens_eval["average_composite_costs"],
                }, f, indent=2)
            logger.info(f"Saved sensitivity analysis to {sens_out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
