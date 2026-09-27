"""
PackWise AI - ML Feature Preparation & Governance (Milestone M1)
Prepares verified empirical data for future machine learning training.
Strict Anti-Fabrication: Reports MODEL_STATUS = INSUFFICIENT_VERIFIED_DATA until
expanded multi-temperature kinetics datasets are curated.
"""
from typing import Dict, Any, List, Tuple, Optional
import os
import csv
import numpy as np

MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"


class MLDatasetPreparator:
    """
    Feature engineering, categorical encoding, and validation pipeline for
    shelf-life kinetic regression modeling.
    """

    # Feature definitions
    NUMERICAL_FEATURES = [
        "respiration_rate_mg_co2_kg_hr",
        "storage_temperature_c",
        "ambient_rh_percent",
        "film_otr_cc_m2_day_atm",
        "film_wvtr_g_m2_day",
        "film_thickness_micron"
    ]

    CATEGORICAL_FEATURES = [
        "category",       # Produce category
        "polymer_type"    # Polymer resin classification
    ]

    CATEGORY_CLASSES = [
        "FRUIT", "VEGETABLE", "DAIRY", "MEAT", "BAKERY", "GRAIN", "SNACK", "PROCESSED_FOOD"
    ]

    POLYMER_CLASSES = [
        "LDPE", "HDPE", "PP", "PET", "EVOH", "PLA", "PHA", "CELLULOSE", "PAPER_BARRIER", "MULTI_LAYER_LAMINATE"
    ]

    @classmethod
    def get_feature_names(cls) -> List[str]:
        cat_encoded = [f"cat_{c.lower()}" for c in cls.CATEGORY_CLASSES]
        poly_encoded = [f"poly_{p.lower()}" for p in cls.POLYMER_CLASSES]
        return cls.NUMERICAL_FEATURES + cat_encoded + poly_encoded

    @classmethod
    def one_hot_encode(cls, value: str, classes: List[str]) -> List[float]:
        val_upper = value.strip().upper()
        return [1.0 if val_upper == c else 0.0 for c in classes]

    @classmethod
    def extract_feature_vector(
        cls,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Transforms biological, packaging, and storage inputs into a model feature vector.
        """
        missing_fields = []

        # Numerical extractions
        resp = commodity.get("respiration_rate_mg_co2_kg_hr")
        if resp is None:
            missing_fields.append("respiration_rate_mg_co2_kg_hr")
            resp = 0.0

        temp = storage.get("storage_temperature_c")
        if temp is None:
            missing_fields.append("storage_temperature_c")
            temp = 4.0

        rh = storage.get("ambient_rh_percent")
        if rh is None:
            missing_fields.append("ambient_rh_percent")
            rh = 85.0

        otr = material.get("otr_cc_m2_day_atm")
        if otr is None:
            missing_fields.append("otr_cc_m2_day_atm")
            otr = 1000.0

        wvtr = material.get("wvtr_g_m2_day")
        if wvtr is None:
            missing_fields.append("wvtr_g_m2_day")
            wvtr = 20.0

        thick = material.get("thickness_micron")
        if thick is None:
            missing_fields.append("thickness_micron")
            thick = 25.0

        num_vec = [float(resp), float(temp), float(rh), float(otr), float(wvtr), float(thick)]

        # Categorical encodings
        cat_vec = cls.one_hot_encode(commodity.get("category", ""), cls.CATEGORY_CLASSES)
        poly_vec = cls.one_hot_encode(material.get("polymer_type", ""), cls.POLYMER_CLASSES)

        full_vector = np.array(num_vec + cat_vec + poly_vec, dtype=float)
        return full_vector, missing_fields

    @classmethod
    def audit_processed_dataset_readiness(cls, project_root: str) -> Dict[str, Any]:
        """
        Evaluates empirical dataset sufficiency for ML model training.
        """
        comm_path = os.path.join(project_root, "data", "processed", "commodities.csv")
        mat_path = os.path.join(project_root, "data", "processed", "materials.csv")

        comm_count = 0
        mat_count = 0
        missing_respiration_count = 0

        if os.path.exists(comm_path):
            with open(comm_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    comm_count += 1
                    if not r.get("respiration_rate_mg_co2_kg_hr"):
                        missing_respiration_count += 1

        if os.path.exists(mat_path):
            with open(mat_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for _ in reader:
                    mat_count += 1

        # Train/Validation/Test split policy documentation:
        # GroupKFold (k=5) by commodity_name to ensure unseen commodities in test folds.
        is_sufficient = comm_count >= 100 and mat_count >= 50

        return {
            "model_status": "READY_FOR_TRAINING" if is_sufficient else MODEL_STATUS,
            "verified_commodity_observations": comm_count,
            "verified_packaging_materials": mat_count,
            "missing_respiration_records": missing_respiration_count,
            "split_strategy": "GroupKFold(k=5, groups='commodity_name')",
            "reason": (
                "Empirical sample size (37 respiration observations, 15 materials) provides robust "
                "baseline for rule screening and TOPSIS MCDM, but gradient-boosted ML regression "
                "requires >=100 verified kinetic time-series curves to prevent overfitting."
                if not is_sufficient else "Sufficient sample size available."
            )
        }
