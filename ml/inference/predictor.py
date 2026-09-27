"""
PackWise AI - ML Inference Engine (Milestone M3)
Executes decoupled runtime inference for food packaging shelf-life prediction.
Strictly adheres to:
  1. Cryptographic SHA-256 model verification before execution
  2. Feature schema validation matching training pipeline
  3. Preprocessing using FeatureEngineer (m3.0.0)
  4. ModelNotAvailableError when MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"
  5. Zero-fabrication: uncertainty_status = "NOT_AVAILABLE" (no fake confidence scores)
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
import numpy as np
import joblib

from ml.registry.model_registry import ModelRegistry, ModelMetadata, ModelStatus
from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.preprocessing.validators import FeatureValidator


class ModelNotAvailableError(Exception):
    """Raised when an inference is requested before a validated model is registered."""
    pass


class ModelChecksumMismatchError(Exception):
    """Raised when a model artifact's SHA-256 hash does not match its registered value."""
    pass


@dataclass
class PredictionResult:
    prediction: float
    model_version: str
    dataset_version: str
    feature_schema_version: str
    model_id: str
    algorithm: str
    uncertainty_status: str = "NOT_AVAILABLE"
    prediction_metadata: Dict[str, Any] = field(default_factory=dict)


class ShelfLifePredictor:
    """
    Runtime inference engine for shelf-life prediction.
    Loads versioned model artifacts, checks SHA-256 integrity, validates input schema,
    and returns predictions with complete provenance metadata.
    """
    def __init__(
        self,
        model_id: Optional[str] = None,
        task: str = "shelf_life_regression",
        registry: Optional[ModelRegistry] = None,
        model_dir: Optional[str] = None
    ):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.registry = registry or ModelRegistry(os.path.join(self.project_root, "ml", "registry"))
        self.model_dir = model_dir or os.path.join(self.project_root, "ml", "models")
        self.task = task
        self.model_id = model_id
        self._loaded_model_payload = None
        self._active_metadata: Optional[ModelMetadata] = None

    def get_model_metadata(self) -> Optional[ModelMetadata]:
        """Retrieves registered model metadata for current task or model_id."""
        if self.model_id:
            return self.registry.get_model(self.model_id)
        # Fallback: search for production model or validated model
        prod = self.registry.get_production_model(self.task)
        if prod:
            return prod
        # Search for any validated model
        for m in self.registry.list_models():
            if m.task == self.task and m.status in [ModelStatus.VALIDATED, ModelStatus.PRODUCTION]:
                return m
        return None

    def is_model_available(self) -> bool:
        """
        Verifies if an eligible, non-blocked model artifact exists and passes checksum validation.
        """
        meta = self.get_model_metadata()
        if not meta:
            return False

        if meta.status in [ModelStatus.BLOCKED, ModelStatus.RETIRED]:
            return False

        if not meta.artifact_path or not os.path.exists(meta.artifact_path):
            return False

        # Verify cryptographic checksum
        return self.registry.verify_artifact_checksum(meta.model_id)

    def _load_model(self) -> None:
        """Loads and verifies model artifact from disk."""
        meta = self.get_model_metadata()
        if not meta:
            raise ModelNotAvailableError(
                "Trained shelf-life model artifact not available [MODEL_STATUS = 'INSUFFICIENT_VERIFIED_DATA']. "
                "Adhering to strict zero-fake-prediction policy until empirical time-series data is verified."
            )

        if meta.status == ModelStatus.BLOCKED:
            raise ModelNotAvailableError(
                f"Model '{meta.model_id}' is BLOCKED [MODEL_STATUS = 'INSUFFICIENT_VERIFIED_DATA']: {meta.notes}"
            )

        if not meta.artifact_path or not os.path.exists(meta.artifact_path):
            raise ModelNotAvailableError(
                f"Model artifact file not found on disk at {meta.artifact_path}."
            )

        # Cryptographic SHA-256 verification
        if not self.registry.verify_artifact_checksum(meta.model_id):
            raise ModelChecksumMismatchError(
                f"SHA-256 checksum verification failed for model {meta.model_id}. "
                "Artifact may have been modified or corrupted."
            )

        payload = joblib.load(meta.artifact_path)
        self._loaded_model_payload = payload
        self._active_metadata = meta

    def predict(
        self,
        features: Union[np.ndarray, Dict[str, Any]],
        commodity_data: Optional[Dict[str, Any]] = None,
        material_data: Optional[Dict[str, Any]] = None,
        storage_data: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Executes shelf-life prediction.
        Raises ModelNotAvailableError if no validated model exists.
        Returns float prediction for backward compatibility.
        """
        res = self.predict_detailed(
            features=features,
            commodity_data=commodity_data,
            material_data=material_data,
            storage_data=storage_data
        )
        return res.prediction

    def predict_detailed(
        self,
        features: Union[np.ndarray, Dict[str, Any]],
        commodity_data: Optional[Dict[str, Any]] = None,
        material_data: Optional[Dict[str, Any]] = None,
        storage_data: Optional[Dict[str, Any]] = None
    ) -> PredictionResult:
        """
        Executes inference and returns full provenance metadata including zero-confidence disclosure.
        """
        if not self.is_model_available():
            raise ModelNotAvailableError(
                "Trained shelf-life model artifact not available [MODEL_STATUS = 'INSUFFICIENT_VERIFIED_DATA']. "
                "Adhering to strict zero-fake-prediction policy until empirical time-series data is verified."
            )

        if self._loaded_model_payload is None:
            self._load_model()

        # Feature preparation and validation
        if isinstance(features, dict) or (commodity_data is not None):
            c_data = commodity_data or features.get("commodity", {})
            m_data = material_data or features.get("material", {})
            s_data = storage_data or features.get("storage", {})

            # Validate physical bounds
            val_report = FeatureValidator.validate_all(c_data, m_data, s_data)
            if not val_report.is_valid:
                raise ValueError(f"Feature validation failed: {val_report.errors}")

            feature_vec = FeatureEngineer.transform_record(c_data, m_data, s_data)
        elif isinstance(features, np.ndarray):
            feature_vec = features
        else:
            raise TypeError("Features must be a numpy ndarray or a dictionary.")

        feature_vec = np.asarray(feature_vec, dtype=float).reshape(1, -1)
        expected_len = len(FeatureEngineer.get_feature_names())
        if feature_vec.shape[1] != expected_len:
            raise ValueError(
                f"Feature vector dimensionality mismatch: Expected {expected_len}, got {feature_vec.shape[1]}."
            )

        model_obj = self._loaded_model_payload.get("model", self._loaded_model_payload)
        pred_raw = model_obj.predict(feature_vec)
        pred_val = float(pred_raw[0]) if hasattr(pred_raw, "__len__") else float(pred_raw)

        return PredictionResult(
            prediction=round(pred_val, 2),
            model_version=self._active_metadata.model_version,
            dataset_version=self._active_metadata.dataset_version,
            feature_schema_version=self._active_metadata.feature_schema_version,
            model_id=self._active_metadata.model_id,
            algorithm=self._active_metadata.algorithm,
            uncertainty_status="NOT_AVAILABLE",
            prediction_metadata={
                "features_used": FeatureEngineer.get_feature_names(),
                "unit": "days",
                "notes": "Deterministic model inference"
            }
        )
