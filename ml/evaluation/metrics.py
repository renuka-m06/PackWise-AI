from typing import Dict
import numpy as np


class ShelfLifeModelEvaluator:
    """
    Standard regression evaluation metrics.
    Only computes metrics from genuine observed test pairs.
    """
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)

        mae = float(np.mean(np.abs(y_true - y_pred)))
        mse = float(np.mean((y_true - y_pred) ** 2))
        rmse = float(np.sqrt(mse))

        # Coefficient of determination R^2
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

        return {
            "mae_days": round(mae, 3),
            "rmse_days": round(rmse, 3),
            "r2_score": round(r2, 4)
        }
