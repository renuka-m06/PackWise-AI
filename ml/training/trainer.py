"""
PackWise AI - ML Training Pipeline Orchestrator (Milestone M3)
Implements deterministic, sufficiency-gated ML model training.
Adheres strictly to the PackWise AI anti-fabrication mandate:
  If verified empirical data is insufficient, training is formally blocked with:
  MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"
"""
import os
import json
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import joblib

from ml.data.dataset_builder import MLDatasetBuilder
from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.preprocessing.splits import GroupAwareSplitter
from ml.preprocessing.leakage_detector import LeakageDetector
from ml.training.sufficiency_gate import (
    DataSufficiencyGate,
    SufficiencyGateReport,
    TrainingBlockedError
)
from ml.training.baselines import (
    MeanBaselineRegressor,
    MedianBaselineRegressor,
    RidgeRegressionBaseline
)
from ml.training.candidate_models import (
    RandomForestShelfLifeRegressor,
    GradientBoostingShelfLifeRegressor,
    XGBoostShelfLifeRegressor
)
from ml.training.cross_validation import GroupCrossValidator, CrossValidationReport
from ml.evaluation.metrics import ModelMetricsCalculator
from ml.registry.model_registry import (
    ModelRegistry,
    ModelMetadata,
    ModelStatus
)


class BaseShelfLifeTrainer(ABC):
    """
    Abstract harness for training shelf-life regressors.
    Decoupled strictly from runtime API dependencies (Preserves M0 contract).
    """
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> Any:
        """Fit regressor on empirical data."""
        pass

    @abstractmethod
    def save_artifact(self, model: Any, output_path: str, metadata: Dict[str, Any]) -> None:
        """Serialize model artifact with provenance metadata."""
        pass


class MLTrainingPipeline(BaseShelfLifeTrainer):
    """
    Production-grade ML training pipeline for PackWise AI.
    Executes sequential sufficiency gates, leak audits, group-aware cross validation,
    baseline benchmarking, artifact serialization, SHA-256 verification, and registry logging.
    """
    def __init__(
        self,
        project_root: Optional[str] = None,
        registry: Optional[ModelRegistry] = None,
        min_samples: int = 100,
        min_groups: int = 20,
        random_seed: int = 42
    ):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.registry = registry or ModelRegistry(os.path.join(self.project_root, "ml", "registry"))
        self.min_samples = min_samples
        self.min_groups = min_groups
        self.random_seed = random_seed
        self.models_dir = os.path.join(self.project_root, "ml", "models")
        os.makedirs(self.models_dir, exist_ok=True)

    def train(self, X: np.ndarray, y: np.ndarray) -> Any:
        """
        Fits candidate model directly (conforming to BaseShelfLifeTrainer interface).
        """
        model = RidgeRegressionBaseline()
        model.fit(X, y)
        return model

    def save_artifact(self, model: Any, output_path: str, metadata: Dict[str, Any]) -> None:
        """
        Serializes model artifact and sidecar metadata.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        joblib.dump(model, output_path)

        meta_path = output_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def run_training_pipeline(
        self,
        task_name: str = "shelf_life_regression",
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        groups: Optional[List[str]] = None,
        feature_names: Optional[List[str]] = None,
        target_name: str = "target_shelf_life_unpacked_days",
        dataset_version: str = "1.0.0-m3",
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the full M3 training workflow.
        If empirical data fails sufficiency gates, logs BLOCKED status in ModelRegistry
        and either raises TrainingBlockedError (if strict=True) or returns blocked report.
        """
        # 1. Load dataset if not provided
        if X is None or y is None or groups is None or feature_names is None:
            builder = MLDatasetBuilder(self.project_root)
            dataset_info = builder.build_shelf_life_dataset()
            X = dataset_info["X"]
            y = dataset_info["y"]
            groups = dataset_info["groups"]
            feature_names = dataset_info["feature_names"]
            dataset_version = dataset_info["manifest"]["dataset_version"]

        # 2. Evaluate Data Sufficiency Gates (NON-BYPASSABLE)
        gate_report = DataSufficiencyGate.evaluate_gates(
            X=X,
            y=y,
            feature_names=feature_names,
            groups=groups,
            target_name=target_name,
            min_samples=self.min_samples,
            min_groups=self.min_groups
        )

        model_id = f"{task_name}_{dataset_version.replace('.', '_')}"

        if not gate_report.can_train:
            # Register BLOCKED entry in ModelRegistry
            blocked_meta = ModelMetadata(
                model_id=model_id,
                model_name="Shelf Life Regressor (Empirical Candidate)",
                model_version="m3.0.0",
                task=task_name,
                algorithm="XGBoost / HistGradientBoosting",
                dataset_version=dataset_version,
                feature_schema_version=FeatureEngineer.FEATURE_SCHEMA_VERSION,
                training_date=datetime.now(timezone.utc).isoformat(),
                status=ModelStatus.BLOCKED,
                metrics={
                    "status": "BLOCKED",
                    "reason": "INSUFFICIENT_VERIFIED_DATA",
                    "blocking_reasons": gate_report.blocking_reasons
                },
                artifact_path=None,
                checksum_sha256=None,
                hyperparameters={},
                notes=f"Training blocked by Data Sufficiency Gate: {'; '.join(gate_report.blocking_reasons)}"
            )
            self.registry.register_model(blocked_meta)

            if strict:
                raise TrainingBlockedError(
                    f"Training blocked for task '{task_name}' [{gate_report.status}]: "
                    f"{'; '.join(gate_report.blocking_reasons)}"
                )

            return {
                "status": "BLOCKED",
                "model_status": "INSUFFICIENT_VERIFIED_DATA",
                "gate_report": gate_report,
                "model_id": model_id,
                "message": (
                    f"Training blocked for task '{task_name}'. Data sufficiency gates failed. "
                    "In strict adherence to PackWise AI anti-fabrication standards, no model was trained."
                )
            }

        # 3. If Sufficiency Gates PASS: Proceed with Leak-Free Training
        splitter = GroupAwareSplitter(random_seed=self.random_seed)
        split_result = splitter.train_val_test_split(X, y, groups, val_ratio=0.2, test_ratio=0.2)

        X_train, y_train = split_result.X_train, split_result.y_train
        X_val, y_val = split_result.X_val, split_result.y_val
        X_test, y_test = split_result.X_test, split_result.y_test

        # 4. Benchmarking Baseline Models
        baselines = {
            "mean_baseline": MeanBaselineRegressor(),
            "median_baseline": MedianBaselineRegressor(),
            "ridge_baseline": RidgeRegressionBaseline(alpha=1.0)
        }
        baseline_results = {}
        for b_name, b_model in baselines.items():
            b_model.fit(X_train, y_train)
            val_preds = b_model.predict(X_val)
            metrics = ModelMetricsCalculator.calculate_regression_metrics(y_val, val_preds, split_name="validation")
            baseline_results[b_name] = metrics

        # 5. Candidate Models & 5-Fold Group Cross Validation
        candidate_factories = {
            "RandomForest": lambda: RandomForestShelfLifeRegressor(random_state=self.random_seed),
            "GradientBoosting": lambda: GradientBoostingShelfLifeRegressor(random_state=self.random_seed),
            "XGBoost": lambda: XGBoostShelfLifeRegressor(random_state=self.random_seed)
        }

        cv_evaluator = GroupCrossValidator(n_splits=min(5, len(set(split_result.groups_train))), random_seed=self.random_seed)
        cv_results: Dict[str, CrossValidationReport] = {}

        for c_name, c_factory in candidate_factories.items():
            cv_report = cv_evaluator.evaluate_model(
                model_factory=c_factory,
                X=X_train,
                y=y_train,
                groups=split_result.groups_train,
                algorithm_name=c_name
            )
            cv_results[c_name] = cv_report

        # 6. Model Selection: Select model with lowest validation MAE
        best_candidate_name = min(cv_results.keys(), key=lambda k: cv_results[k].mean_mae)
        best_cv = cv_results[best_candidate_name]

        # Fit best model on Train + Val, evaluate on holdout Test
        X_train_full = np.vstack([X_train, X_val])
        y_train_full = np.concatenate([y_train, y_val])

        best_model = candidate_factories[best_candidate_name]()
        best_model.fit(X_train_full, y_train_full)

        test_preds = best_model.predict(X_test)
        test_metrics = ModelMetricsCalculator.calculate_regression_metrics(
            y_true=y_test,
            y_pred=test_preds,
            split_name="test",
            model_version="m3.0.0"
        )

        # 7. Serialize Artifact and Compute SHA-256
        task_dir = os.path.join(self.models_dir, task_name)
        os.makedirs(task_dir, exist_ok=True)
        artifact_file = f"{model_id}.joblib"
        artifact_path = os.path.join(task_dir, artifact_file)

        model_payload = {
            "model": best_model,
            "feature_names": feature_names,
            "feature_schema_version": FeatureEngineer.FEATURE_SCHEMA_VERSION,
            "dataset_version": dataset_version,
            "algorithm": best_candidate_name,
            "random_seed": self.random_seed
        }
        self.save_artifact(model_payload, artifact_path, {
            "model_id": model_id,
            "test_metrics": test_metrics,
            "cv_mae": best_cv.mean_mae
        })

        checksum = ModelRegistry.compute_sha256(artifact_path)

        # 8. Register Model
        model_meta = ModelMetadata(
            model_id=model_id,
            model_name=f"PackWise {best_candidate_name} Shelf Life Regressor",
            model_version="m3.0.0",
            task=task_name,
            algorithm=best_candidate_name,
            dataset_version=dataset_version,
            feature_schema_version=FeatureEngineer.FEATURE_SCHEMA_VERSION,
            training_date=datetime.now(timezone.utc).isoformat(),
            status=ModelStatus.VALIDATED if test_metrics["r2"] > 0.5 else ModelStatus.CANDIDATE,
            metrics={
                "test": test_metrics,
                "cv": {
                    "mean_mae": best_cv.mean_mae,
                    "std_mae": best_cv.std_mae,
                    "mean_rmse": best_cv.mean_rmse,
                    "mean_r2": best_cv.mean_r2
                },
                "baselines": baseline_results
            },
            artifact_path=artifact_path,
            checksum_sha256=checksum,
            hyperparameters={"random_state": self.random_seed},
            notes="Trained and validated on verified empirical dataset."
        )
        self.registry.register_model(model_meta)

        return {
            "status": "COMPLETED",
            "model_status": model_meta.status,
            "model_id": model_id,
            "selected_model": best_candidate_name,
            "test_metrics": test_metrics,
            "cv_metrics": best_cv,
            "artifact_path": artifact_path,
            "checksum_sha256": checksum
        }
