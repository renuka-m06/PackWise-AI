import os
from typing import Dict, Any, Optional
import numpy as np


class ModelNotAvailableError(Exception):
    """Raised when an inference is requested before a trained model is registered."""
    pass


class ShelfLifePredictor:
    """
    Runtime inference engine for shelf-life prediction.
    Loads versioned model artifacts and executes forward passes.
    """
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "models"
        )
        self.model = None
        self.metadata = None

    def is_model_available(self) -> bool:
        """Checks if a verified trained model artifact exists in model registry."""
        model_path = os.path.join(self.model_dir, "shelf_life_regressor.joblib")
        return os.path.exists(model_path)

    def predict(self, feature_vector: np.ndarray) -> float:
        """
        Executes shelf-life prediction.
        Raises ModelNotAvailableError in Milestone M0 where empirical training is pending.
        """
        if not self.is_model_available():
            raise ModelNotAvailableError(
                "Trained shelf-life model artifact not available. "
                "Adhering to strict zero-fake-prediction policy until Phase 1 data ingestion."
            )
        
        # When model is loaded in Phase 1:
        # return float(self.model.predict(feature_vector.reshape(1, -1))[0])
        raise NotImplementedError("Pending Phase 1 dataset ingestion.")
