"""
PackWise AI - Feature Engineering & Transformation Engine (Milestone M3)
Deterministic, documented transformations for biological, logistics, and barrier features.
Strictly decoupled from runtime API routes and free of target leakage.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import math


@dataclass
class FeatureDefinition:
    feature_name: str
    description: str
    source_fields: List[str]
    transformation: str
    unit: str
    version: str = "m3.0.0"


class FeatureEngineer:
    """
    Transforms raw commodity, packaging material, and storage logistics data
    into a model-ready numerical feature matrix with documented provenance.
    """
    FEATURE_SCHEMA_VERSION = "m3.0.0"

    CATEGORY_CLASSES = ["FRUIT", "VEGETABLE", "DAIRY", "MEAT", "BAKERY", "GRAIN", "SNACK", "PROCESSED_FOOD"]
    POLYMER_CLASSES = ["LDPE", "HDPE", "PP", "PET", "EVOH", "PLA", "PHA", "CELLULOSE", "PAPER_BARRIER", "MULTI_LAYER_LAMINATE"]

    DEFINITIONS: List[FeatureDefinition] = [
        FeatureDefinition(
            feature_name="log_respiration_rate",
            description="Base-10 log of commodity respiration rate to stabilize exponential temperature kinetics",
            source_fields=["respiration_rate_mg_co2_kg_hr"],
            transformation="log10(max(respiration_rate, 0.0) + 1.0)",
            unit="log10(mg CO2/(kg*hr))"
        ),
        FeatureDefinition(
            feature_name="storage_temperature_c",
            description="Ambient cold chain distribution temperature in Celsius",
            source_fields=["storage_temperature_c"],
            transformation="identity",
            unit="°C"
        ),
        FeatureDefinition(
            feature_name="ambient_rh_percent",
            description="Ambient relative humidity percentage",
            source_fields=["ambient_rh_percent"],
            transformation="identity",
            unit="%"
        ),
        FeatureDefinition(
            feature_name="log_otr",
            description="Base-10 log of Oxygen Transmission Rate under ASTM D3985",
            source_fields=["otr_cc_m2_day_atm"],
            transformation="log10(max(otr, 0.01) + 1.0)",
            unit="log10(cc/(m2*day*atm))"
        ),
        FeatureDefinition(
            feature_name="log_wvtr",
            description="Base-10 log of Water Vapor Transmission Rate under ASTM F1249",
            source_fields=["wvtr_g_m2_day"],
            transformation="log10(max(wvtr, 0.01) + 1.0)",
            unit="log10(g/(m2*day))"
        ),
        FeatureDefinition(
            feature_name="film_thickness_micron",
            description="Packaging barrier film gauge in microns",
            source_fields=["thickness_micron"],
            transformation="identity",
            unit="um"
        ),
        FeatureDefinition(
            feature_name="barrier_ratio_otr_wvtr",
            description="Ratio of oxygen transmission to moisture transmission",
            source_fields=["otr_cc_m2_day_atm", "wvtr_g_m2_day"],
            transformation="otr / max(wvtr, 0.1)",
            unit="ratio"
        ),
        FeatureDefinition(
            feature_name="water_activity_aw",
            description="Thermodynamic water activity indicating microbial susceptibility",
            source_fields=["water_activity_aw"],
            transformation="identity",
            unit="aw"
        ),
        FeatureDefinition(
            feature_name="native_pH",
            description="Native commodity pH determining microbial and enzymatic boundary",
            source_fields=["pH"],
            transformation="identity",
            unit="pH"
        ),
        FeatureDefinition(
            feature_name="is_biodegradable_flag",
            description="Binary indicator for certified compostable/biodegradable polymer",
            source_fields=["is_biodegradable"],
            transformation="1.0 if true else 0.0",
            unit="boolean"
        ),
        FeatureDefinition(
            feature_name="recyclability_code",
            description="Resin Identification Code (1 to 7)",
            source_fields=["recyclability_code"],
            transformation="float(code)",
            unit="integer_code"
        ),
    ]

    @classmethod
    def get_feature_names(cls) -> List[str]:
        base_names = [f.feature_name for f in cls.DEFINITIONS]
        cat_names = [f"cat_{c.lower()}" for c in cls.CATEGORY_CLASSES]
        poly_names = [f"poly_{p.lower()}" for p in cls.POLYMER_CLASSES]
        return base_names + cat_names + poly_names

    @classmethod
    def transform_record(
        cls,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> np.ndarray:
        """
        Extracts ordered, deterministic feature vector from commodity, material, and storage dictionaries.
        """
        # 1. Numerical extraction with deterministic defaults
        resp = float(commodity.get("respiration_rate_mg_co2_kg_hr") or 0.0)
        temp = float(storage.get("storage_temperature_c", storage.get("temperature_c", 4.0)))
        rh = float(storage.get("ambient_rh_percent", storage.get("relative_humidity_pct", 85.0)))
        otr = float(material.get("otr_cc_m2_day_atm") or 1000.0)
        wvtr = float(material.get("wvtr_g_m2_day") or 20.0)
        thick = float(material.get("thickness_micron") or 25.0)
        aw = float(commodity.get("water_activity_aw") or 0.95)
        ph = float(commodity.get("pH") or 6.0)
        is_bio = 1.0 if material.get("is_biodegradable", False) else 0.0
        recyc = float(material.get("recyclability_code") or 7.0)

        # 2. Mathematical transformations
        log_resp = math.log10(max(resp, 0.0) + 1.0)
        log_otr = math.log10(max(otr, 0.01) + 1.0)
        log_wvtr = math.log10(max(wvtr, 0.01) + 1.0)
        barrier_ratio = otr / max(wvtr, 0.1)

        vector_base = [
            log_resp,
            temp,
            rh,
            log_otr,
            log_wvtr,
            thick,
            barrier_ratio,
            aw,
            ph,
            is_bio,
            recyc
        ]

        # 3. Categorical one-hot encoding
        cat_str = str(commodity.get("category", "")).upper()
        cat_vec = [1.0 if cat_str == c else 0.0 for c in cls.CATEGORY_CLASSES]

        poly_str = str(material.get("polymer_type", "")).upper()
        poly_vec = [1.0 if poly_str == p else 0.0 for p in cls.POLYMER_CLASSES]

        return np.array(vector_base + cat_vec + poly_vec, dtype=float)

    @classmethod
    def get_feature_documentation(cls) -> List[Dict[str, Any]]:
        return [
            {
                "feature_name": f.feature_name,
                "description": f.description,
                "source_fields": f.source_fields,
                "transformation": f.transformation,
                "unit": f.unit,
                "version": f.version
            }
            for f in cls.DEFINITIONS
        ]
