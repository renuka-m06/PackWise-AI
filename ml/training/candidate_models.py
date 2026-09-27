"""
PackWise AI - Candidate ML Models Architecture (Milestone M3)
Implements candidate regressors (RandomForest, HistGradientBoosting, XGBoost)
decoupled from runtime APIs.
"""
from typing import Dict, Any, Optional
import numpy as np


class RandomForestShelfLifeRegressor:
    """Random Forest regressor candidate."""
    def __init__(self, n_estimators: int = 50, max_depth: int = 5, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestShelfLifeRegressor":
        try:
            from sklearn.ensemble import RandomForestRegressor
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=self.random_state
            )
            self.model.fit(X, y)
        except ImportError:
            raise RuntimeError("scikit-learn is required to train RandomForestShelfLifeRegressor.")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.model is not None, "Model must be fitted before predict."
        return self.model.predict(X)


class GradientBoostingShelfLifeRegressor:
    """HistGradientBoosting regressor candidate with native monotonicity constraint capability."""
    def __init__(self, max_iter: int = 50, max_depth: int = 4, random_state: int = 42):
        self.max_iter = max_iter
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GradientBoostingShelfLifeRegressor":
        try:
            from sklearn.ensemble import HistGradientBoostingRegressor
            self.model = HistGradientBoostingRegressor(
                max_iter=self.max_iter,
                max_depth=self.max_depth,
                random_state=self.random_state
            )
            self.model.fit(X, y)
        except ImportError:
            raise RuntimeError("scikit-learn is required to train GradientBoostingShelfLifeRegressor.")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.model is not None, "Model must be fitted before predict."
        return self.model.predict(X)


class XGBoostShelfLifeRegressor:
    """XGBoost regressor candidate with graceful fallback if xgboost C-library is missing."""
    def __init__(self, n_estimators: int = 50, max_depth: int = 4, learning_rate: float = 0.1, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model = None
        self.backend = "xgboost"

    def fit(self, X: np.ndarray, y: np.ndarray) -> "XGBoostShelfLifeRegressor":
        try:
            import xgboost as xgb
            self.model = xgb.XGBRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
                verbosity=0
            )
            self.backend = "xgboost"
        except (ImportError, Exception):
            # Fallback to HistGradientBoosting if xgboost binary fails on Windows
            from sklearn.ensemble import HistGradientBoostingRegressor
            self.model = HistGradientBoostingRegressor(
                max_iter=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state
            )
            self.backend = "hist_gradient_boosting_fallback"

        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.model is not None, "Model must be fitted before predict."
        return self.model.predict(X)
