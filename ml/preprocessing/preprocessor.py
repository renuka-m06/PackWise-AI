from typing import Dict, Any, List
import numpy as np


class ShelfLifeFeaturePreprocessor:
    """
    Feature transformation pipeline for packaging shelf-life regression.
    Transforms raw biological and film properties into model-ready tensors.
    """
    FEATURE_NAMES = [
        "respiration_rate",
        "storage_temperature",
        "ambient_rh",
        "film_otr",
        "film_wvtr",
        "film_thickness"
    ]

    def extract_features(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> np.ndarray:
        """
        Extracts ordered numerical feature vector.
        """
        vector = [
            float(commodity.get("respiration_rate_mg_co2_kg_hr") or 0.0),
            float(storage.get("storage_temperature_c") or 4.0),
            float(storage.get("ambient_rh_percent") or 85.0),
            float(material.get("otr_cc_m2_day_atm") or 1000.0),
            float(material.get("wvtr_g_m2_day") or 20.0),
            float(material.get("thickness_micron") or 25.0),
        ]
        return np.array(vector, dtype=float)
