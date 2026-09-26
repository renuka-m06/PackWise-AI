import os
from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class BaseShelfLifeTrainer(ABC):
    """
    Abstract harness for training shelf-life regressors.
    Decoupled strictly from runtime API dependencies.
    """
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> Any:
        """Fit regressor on empirical data."""
        pass

    @abstractmethod
    def save_artifact(self, model: Any, output_path: str, metadata: Dict[str, Any]) -> None:
        """Serialize model artifact with provenance metadata."""
        pass
