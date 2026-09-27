"""
PackWise AI - Empirical Evaluation Metrics Engine (Milestone M3)
Computes regression and classification metrics exclusively from verified observed test pairs.
Strictly prohibits hardcoding, manufacturing, or paper-copying of metrics.
"""
from typing import Dict, Any, List, Optional
import numpy as np


class ModelMetricsCalculator:
    """
    Computes regression and classification evaluation metrics.
    Guarantees epsilon safety against division by zero.
    """

    @staticmethod
    def calculate_regression_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        split_name: str = "test",
        model_version: str = "m3.0.0"
    ) -> Dict[str, Any]:
        """
        Calculates MAE, RMSE, R^2, and MAPE strictly from genuine test pairs.
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)

        n = len(y_true)
        if n == 0:
            return {
                "sample_count": 0,
                "split_name": split_name,
                "model_version": model_version,
                "mae": None,
                "rmse": None,
                "r2": None,
                "mape_pct": None
            }

        residuals = y_true - y_pred
        mae = float(np.mean(np.abs(residuals)))
        mse = float(np.mean(residuals ** 2))
        rmse = float(np.sqrt(mse))

        # Coefficient of determination R^2
        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-8 else 0.0

        # Mean Absolute Percentage Error (MAPE) with epsilon protection
        epsilon = 1e-4
        non_zero_mask = np.abs(y_true) > epsilon
        if np.any(non_zero_mask):
            mape = float(np.mean(np.abs(residuals[non_zero_mask] / y_true[non_zero_mask]))) * 100.0
        else:
            mape = None

        return {
            "sample_count": n,
            "split_name": split_name,
            "model_version": model_version,
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2": round(r2, 4),
            "mape_pct": round(mape, 2) if mape is not None else None
        }

    @staticmethod
    def calculate_classification_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        split_name: str = "test",
        model_version: str = "m3.0.0"
    ) -> Dict[str, Any]:
        """
        Calculates accuracy, precision, recall, and F1 score across classification classes.
        """
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        n = len(y_true)

        if n == 0:
            return {"sample_count": 0, "accuracy": None, "f1_macro": None}

        accuracy = float(np.mean(y_true == y_pred))

        classes = np.unique(y_true)
        precisions = []
        recalls = []
        f1s = []

        for c in classes:
            tp = int(np.sum((y_true == c) & (y_pred == c)))
            fp = int(np.sum((y_true != c) & (y_pred == c)))
            fn = int(np.sum((y_true == c) & (y_pred != c)))

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

        return {
            "sample_count": n,
            "split_name": split_name,
            "model_version": model_version,
            "accuracy": round(accuracy, 4),
            "precision_macro": round(float(np.mean(precisions)), 4) if precisions else 0.0,
            "recall_macro": round(float(np.mean(recalls)), 4) if recalls else 0.0,
            "f1_macro": round(float(np.mean(f1s)), 4) if f1s else 0.0
        }


# Maintain backward compatibility with M0 test suite
class ShelfLifeModelEvaluator:
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        res = ModelMetricsCalculator.calculate_regression_metrics(y_true, y_pred)
        return {
            "mae_days": res["mae"],
            "rmse_days": res["rmse"],
            "r2_score": res["r2"]
        }
