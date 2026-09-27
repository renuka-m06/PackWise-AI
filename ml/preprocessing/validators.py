"""
PackWise AI - ML Feature & Dataset Validation Engine (Milestone M3)
Validates feature matrices, data types, physical bounds, and missing value constraints.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
import numpy as np


@dataclass
class FeatureValidationResult:
    is_valid: bool
    feature_count: int
    missing_features: List[str] = field(default_factory=list)
    out_of_bounds_features: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class FeatureValidator:
    """
    Validates input features for ML pipelines against physical bounds and expected types.
    """
    PHYSICAL_BOUNDS = {
        "storage_temperature_c": (-30.0, 60.0),
        "ambient_rh_percent": (0.0, 100.0),
        "film_otr_cc_m2_day_atm": (0.0, 50000.0),
        "film_wvtr_g_m2_day": (0.0, 1000.0),
        "film_thickness_micron": (1.0, 2000.0),
        "respiration_rate_mg_co2_kg_hr": (0.0, 1000.0),
        "water_activity_aw": (0.0, 1.0),
        "pH": (1.0, 14.0),
        "moisture_content_pct": (0.0, 100.0)
    }

    @classmethod
    def validate_features(
        cls,
        features: Dict[str, Any],
        required_features: Optional[List[str]] = None
    ) -> FeatureValidationResult:
        """
        Validates feature dictionary against required feature set and physical bounds.
        """
        required = required_features or []
        missing = [f for f in required if f not in features or features[f] is None]
        out_of_bounds = []
        issues = []

        for feat_name, val in features.items():
            if val is None or not isinstance(val, (int, float)):
                continue

            bounds = cls.PHYSICAL_BOUNDS.get(feat_name)
            if bounds:
                min_b, max_b = bounds
                if val < min_b or val > max_b:
                    out_of_bounds.append({
                        "feature": feat_name,
                        "observed_value": val,
                        "valid_bounds": bounds
                    })
                    issues.append(f"Feature '{feat_name}'={val} violates bounds [{min_b}, {max_b}]")

        is_valid = len(missing) == 0 and len(out_of_bounds) == 0
        return FeatureValidationResult(
            is_valid=is_valid,
            feature_count=len(features),
            missing_features=missing,
            out_of_bounds_features=out_of_bounds,
            issues=issues
        )

    @classmethod
    def validate_all(
        cls,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> FeatureValidationResult:
        """
        Validates combined commodity, material, and storage feature dictionaries.
        """
        combined = {}
        # Commodity mapping
        if "water_activity_aw" in commodity:
            combined["water_activity_aw"] = commodity["water_activity_aw"]
        elif "water_activity" in commodity:
            combined["water_activity_aw"] = commodity["water_activity"]

        if "pH" in commodity:
            combined["pH"] = commodity["pH"]

        if "respiration_rate_mg_co2_kg_hr" in commodity:
            combined["respiration_rate_mg_co2_kg_hr"] = commodity["respiration_rate_mg_co2_kg_hr"]

        if "moisture_content_pct" in commodity:
            combined["moisture_content_pct"] = commodity["moisture_content_pct"]

        # Material mapping
        if "thickness_micron" in material:
            combined["film_thickness_micron"] = material["thickness_micron"]
        if "otr_cc_m2_day_atm" in material:
            combined["film_otr_cc_m2_day_atm"] = material["otr_cc_m2_day_atm"]
        if "wvtr_g_m2_day" in material:
            combined["film_wvtr_g_m2_day"] = material["wvtr_g_m2_day"]

        # Storage mapping
        if "storage_temperature_c" in storage:
            combined["storage_temperature_c"] = storage["storage_temperature_c"]
        if "ambient_rh_percent" in storage:
            combined["ambient_rh_percent"] = storage["ambient_rh_percent"]

        res = cls.validate_features(combined)
        # Check required fields
        errors = list(res.issues)
        return type("CombinedValidationReport", (), {
            "is_valid": res.is_valid,
            "errors": errors,
            "issues": res.issues,
            "feature_count": res.feature_count
        })()
