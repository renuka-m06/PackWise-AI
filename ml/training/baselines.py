"""
PackWise AI - Baseline ML Models (Milestone M3)
Implements statistical and simple linear baselines to benchmark candidate complex models.
Prevents ungrounded claims of model superiority without empirical measurement.
"""
from typing import Dict, Any, Optional
import numpy as np


class MeanBaselineRegressor:
    """Predicts empirical mean of training targets."""
    def __init__(self):
        self.mean_value_: Optional[float] = None
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MeanBaselineRegressor":
        assert len(y) > 0, "Cannot fit on empty target vector."
        self.mean_value_ = float(np.mean(y))
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.is_fitted, "Model must be fitted before predict."
        return np.full(shape=(len(X),), fill_value=self.mean_value_, dtype=float)


class MedianBaselineRegressor:
    """Predicts empirical median of training targets (robust to extreme shelf-life outliers)."""
    def __init__(self):
        self.median_value_: Optional[float] = None
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MedianBaselineRegressor":
        assert len(y) > 0, "Cannot fit on empty target vector."
        self.median_value_ = float(np.median(y))
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.is_fitted, "Model must be fitted before predict."
        return np.full(shape=(len(X),), fill_value=self.median_value_, dtype=float)


class RidgeRegressionBaseline:
    """
    Closed-form L2 regularized linear regression baseline:
    w = (X^T X + alpha * I)^(-1) X^T y
    """
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.weights_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeRegressionBaseline":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n, p = X.shape

        assert n >= 2, "Need at least 2 samples to fit ridge baseline."

        # Center X and y
        x_mean = np.mean(X, axis=0)
        y_mean = float(np.mean(y))

        X_centered = X - x_mean
        y_centered = y - y_mean

        # Regularized normal equations
        reg_matrix = self.alpha * np.eye(p)
        A = X_centered.T @ X_centered + reg_matrix
        b = X_centered.T @ y_centered

        try:
            self.weights_ = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            self.weights_ = np.linalg.pinv(A) @ b

        self.intercept_ = y_mean - float(x_mean @ self.weights_)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.is_fitted, "Model must be fitted before predict."
        X = np.asarray(X, dtype=float)
        return X @ self.weights_ + self.intercept_


class MajorityClassBaseline:
    """Predicts most frequent class from training labels."""
    def __init__(self):
        self.majority_class_: Any = None
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MajorityClassBaseline":
        assert len(y) > 0, "Cannot fit on empty labels."
        vals, counts = np.unique(y, return_counts=True)
        self.majority_class_ = vals[np.argmax(counts)]
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.is_fitted, "Model must be fitted before predict."
        return np.full(shape=(len(X),), fill_value=self.majority_class_)
