"""
PackWise AI - Group-Aware Cross-Validation Engine (Milestone M3)
Executes deterministic entity-grouped cross-validation, preventing duplicate
or near-identical commodity measurements from leaking across folds.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import numpy as np

from ml.preprocessing.splits import GroupAwareSplitter
from ml.evaluation.metrics import ModelMetricsCalculator


@dataclass
class CrossValidationReport:
    algorithm_name: str
    fold_count: int
    mean_mae: float
    std_mae: float
    mean_rmse: float
    std_rmse: float
    mean_r2: float
    std_r2: float
    fold_metrics: List[Dict[str, Any]] = field(default_factory=list)


class GroupCrossValidator:
    """
    Evaluates regression models using GroupKFold cross-validation.
    """
    def __init__(self, n_splits: int = 5, random_seed: int = 42):
        self.n_splits = n_splits
        self.splitter = GroupAwareSplitter(random_seed=random_seed)

    def evaluate_model(
        self,
        model_factory,
        X: np.ndarray,
        y: np.ndarray,
        groups: List[str],
        algorithm_name: str = "CandidateModel"
    ) -> CrossValidationReport:
        splits = self.splitter.get_k_fold_grouped_splits(groups, n_splits=self.n_splits)

        maes = []
        rmses = []
        r2s = []
        fold_metrics = []

        for fold_idx, (train_idx, test_idx) in enumerate(splits, 1):
            if len(train_idx) == 0 or len(test_idx) == 0:
                continue

            X_tr, y_tr = X[train_idx], y[train_idx]
            X_te, y_te = X[test_idx], y[test_idx]

            # Clone/instantiate fresh model
            model = model_factory()
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)

            metrics = ModelMetricsCalculator.calculate_regression_metrics(
                y_true=y_te,
                y_pred=preds,
                split_name=f"fold_{fold_idx}"
            )
            fold_metrics.append(metrics)
            if metrics["mae"] is not None:
                maes.append(metrics["mae"])
            if metrics["rmse"] is not None:
                rmses.append(metrics["rmse"])
            if metrics["r2"] is not None:
                r2s.append(metrics["r2"])

        return CrossValidationReport(
            algorithm_name=algorithm_name,
            fold_count=len(fold_metrics),
            mean_mae=round(float(np.mean(maes)), 3) if maes else 0.0,
            std_mae=round(float(np.std(maes)), 3) if maes else 0.0,
            mean_rmse=round(float(np.mean(rmses)), 3) if rmses else 0.0,
            std_rmse=round(float(np.std(rmses)), 3) if rmses else 0.0,
            mean_r2=round(float(np.mean(r2s)), 4) if r2s else 0.0,
            std_r2=round(float(np.std(r2s)), 4) if r2s else 0.0,
            fold_metrics=fold_metrics
        )
