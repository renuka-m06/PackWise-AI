"""
PackWise AI - ML Dataset Builder & Manifest Generator (Milestone M3)
Assembles leak-free, version-controlled ML dataset matrices with SHA-256 cryptographic checksums.
"""
import os
import csv
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
import numpy as np

from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.preprocessing.leakage_detector import LeakageDetector


class MLDatasetBuilder:
    """
    Builds reproducible ML training datasets from verified empirical sources,
    enforcing zero-leakage and computing SHA-256 checksums.
    """
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.processed_dir = os.path.join(project_root, "data", "processed")
        self.ml_data_dir = os.path.join(project_root, "ml", "data")
        os.makedirs(self.ml_data_dir, exist_ok=True)

    def build_shelf_life_dataset(self) -> Dict[str, Any]:
        """
        Builds feature matrix X and target vector y for shelf life prediction.
        """
        comm_path = os.path.join(self.processed_dir, "commodities.csv")
        mat_path = os.path.join(self.processed_dir, "materials.csv")

        # Load materials
        materials = []
        if os.path.exists(mat_path):
            with open(mat_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    materials.append(r)

        feature_names = FeatureEngineer.get_feature_names()
        target_name = "target_shelf_life_unpacked_days"

        # Leakage audit assertion
        LeakageDetector.assert_no_leakage(feature_names, target_name)

        X_rows = []
        y_rows = []
        groups = []
        row_records = []

        if os.path.exists(comm_path):
            with open(comm_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    shelf_str = r.get(target_name)
                    if not shelf_str or not shelf_str.strip():
                        continue

                    try:
                        shelf_val = float(shelf_str)
                    except ValueError:
                        continue

                    c_name = r.get("commodity_name", "Unknown")
                    storage = {
                        "storage_temperature_c": float(r.get("observation_temperature_c") or 4.0),
                        "ambient_rh_percent": float(r.get("optimal_rh_min_percent") or 85.0)
                    }

                    # Use nominal packaging representation
                    mat_rep = materials[0] if materials else {}

                    vec = FeatureEngineer.transform_record(r, mat_rep, storage)
                    X_rows.append(vec)
                    y_rows.append(shelf_val)
                    groups.append(c_name)
                    row_records.append({
                        "commodity_name": c_name,
                        "temperature_c": storage["storage_temperature_c"],
                        "shelf_life_days": shelf_val
                    })

        X = np.array(X_rows, dtype=float) if X_rows else np.empty((0, len(feature_names)))
        y = np.array(y_rows, dtype=float) if y_rows else np.empty((0,))

        # Save numpy dataset
        npz_path = os.path.join(self.ml_data_dir, "shelf_life_empirical_v1.npz")
        np.savez_compressed(npz_path, X=X, y=y, groups=np.array(groups), feature_names=np.array(feature_names))

        # Compute SHA-256
        hasher = hashlib.sha256()
        with open(npz_path, "rb") as f:
            hasher.update(f.read())
        checksum = hasher.hexdigest()

        manifest = {
            "dataset_name": "shelf_life_empirical_dataset",
            "dataset_version": "1.0.0-m3",
            "source_dataset_version": "1.0.0-M1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "feature_schema_version": FeatureEngineer.FEATURE_SCHEMA_VERSION,
            "target_definition": target_name,
            "processing_version": "m3.0.0",
            "row_count": len(X),
            "feature_count": len(feature_names),
            "unique_groups_count": len(set(groups)),
            "artifact_file": "shelf_life_empirical_v1.npz",
            "checksum_sha256": checksum
        }

        manifest_path = os.path.join(self.ml_data_dir, "dataset_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return {
            "X": X,
            "y": y,
            "groups": groups,
            "feature_names": feature_names,
            "manifest": manifest,
            "manifest_path": manifest_path
        }
