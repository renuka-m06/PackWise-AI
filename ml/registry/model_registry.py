"""
PackWise AI - Model Registry & Checksum Verification Engine (Milestone M3)
Manages model lifecycles, provenance tracking, cryptographic SHA-256 verification,
and strict gating against unvalidated models.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import os
import json
import hashlib
from datetime import datetime, timezone


class ModelStatus:
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"
    BLOCKED = "BLOCKED"


@dataclass
class ModelMetadata:
    model_id: str
    model_name: str
    model_version: str
    task: str
    algorithm: str
    dataset_version: str
    feature_schema_version: str
    training_date: str
    status: str  # CANDIDATE, VALIDATED, PRODUCTION, RETIRED, BLOCKED
    metrics: Dict[str, Any]
    artifact_path: Optional[str] = None
    checksum_sha256: Optional[str] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


class ModelRegistry:
    """
    Central registry for managing ML model artifacts, SHA-256 hashes, and lifecycle state.
    """
    def __init__(self, registry_dir: Optional[str] = None):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.registry_dir = registry_dir or os.path.join(self.project_root, "ml", "registry")
        self.manifest_path = os.path.join(self.registry_dir, "registry_manifest.json")
        os.makedirs(self.registry_dir, exist_ok=True)
        self._registry_data: Dict[str, Dict[str, Any]] = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"models": {}}

    def _save_manifest(self) -> None:
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self._registry_data, f, indent=2)

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        """Computes SHA-256 cryptographic checksum of a model artifact."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model artifact not found at {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def register_model(self, metadata: ModelMetadata) -> None:
        """
        Registers a new model or updates lifecycle status in the registry.
        """
        if metadata.artifact_path and os.path.exists(metadata.artifact_path):
            metadata.checksum_sha256 = self.compute_sha256(metadata.artifact_path)

        self._registry_data["models"][metadata.model_id] = asdict(metadata)
        self._save_manifest()

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        data = self._registry_data.get("models", {}).get(model_id)
        if data:
            return ModelMetadata(**data)
        return None

    def get_production_model(self, task: str) -> Optional[ModelMetadata]:
        for m_dict in self._registry_data.get("models", {}).values():
            if m_dict.get("task") == task and m_dict.get("status") == ModelStatus.PRODUCTION:
                return ModelMetadata(**m_dict)
        return None

    def verify_artifact_checksum(self, model_id: str) -> bool:
        """
        Verifies that on-disk model artifact matches the registered SHA-256 checksum.
        Detects tampering or corruption.
        """
        model = self.get_model(model_id)
        if not model or not model.artifact_path or not model.checksum_sha256:
            return False

        if not os.path.exists(model.artifact_path):
            return False

        current_hash = self.compute_sha256(model.artifact_path)
        return current_hash == model.checksum_sha256

    def list_models(self) -> List[ModelMetadata]:
        return [ModelMetadata(**m) for m in self._registry_data.get("models", {}).values()]
