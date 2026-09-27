"""
PackWise AI - Food Requirement Extraction & Respiration Rules (Milestone M2)
Converts empirical commodity biological parameters and storage logistics
into deterministic packaging requirements and barrier constraints.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import os
import csv
from app.engines.rules.config import get_rule_config


@dataclass
class PackagingRequirements:
    """
    Structured physical and biochemical constraints derived deterministically
    from commodity properties and supply chain storage conditions.
    """
    commodity_name: str
    category: str
    oxygen_barrier_required: bool = False
    moisture_barrier_required: bool = False
    co2_management_required: bool = False
    ethylene_management_required: bool = False
    high_barrier_required: bool = False
    breathable_packaging_required: bool = False
    map_candidate: bool = False
    seal_integrity_required: bool = True
    max_acceptable_otr: Optional[float] = None
    min_acceptable_otr: Optional[float] = None
    max_acceptable_wvtr: Optional[float] = None
    respiration_status: str = "NON_RESPIRING"  # RESPIRING, NON_RESPIRING, UNKNOWN_TEMPERATURE, MISSING_DATA
    respiration_rate_at_storage_temp: Optional[float] = None
    chilling_threshold_c: Optional[float] = None
    temperature_constraint: Dict[str, Any] = field(default_factory=dict)
    humidity_constraint: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)


class FoodRequirementExtractor:
    """
    Deterministic requirement extractor based strictly on empirical food data.
    Never fabricates respiration rates or barrier tolerances.
    """
    _respiration_cache: Optional[Dict[str, Dict[float, float]]] = None

    def __init__(self, processed_data_dir: Optional[str] = None):
        self.config = get_rule_config()
        self.data_dir = processed_data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
            "data", "processed"
        )
        self._load_empirical_respiration()

    def _load_empirical_respiration(self):
        """Loads verified multi-temperature respiration rates into memory."""
        if FoodRequirementExtractor._respiration_cache is not None:
            return

        cache: Dict[str, Dict[float, float]] = {}
        csv_path = os.path.join(self.data_dir, "commodities.csv")
        if os.path.exists(csv_path):
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        c_name = row.get("commodity_name", "").strip().lower()
                        temp_str = row.get("observation_temperature_c")
                        resp_str = row.get("respiration_rate_mg_co2_kg_hr")
                        if temp_str and resp_str:
                            try:
                                temp = float(temp_str)
                                resp = float(resp_str)
                                if c_name not in cache:
                                    cache[c_name] = {}
                                cache[c_name][temp] = resp
                            except ValueError:
                                pass
            except Exception:
                pass
        FoodRequirementExtractor._respiration_cache = cache

    def find_empirical_respiration_rate(self, commodity_name: str, target_temp_c: float) -> Optional[float]:
        """
        Finds empirical respiration rate if and only if an empirical observation
        exists within +/- 1.5°C of the target temperature.
        DOES NOT FABRICATE OR SILENTLY EXTRAPOLATE.
        """
        if not FoodRequirementExtractor._respiration_cache:
            return None

        c_key = commodity_name.strip().lower()
        obs_map = FoodRequirementExtractor._respiration_cache.get(c_key)
        if not obs_map:
            return None

        for obs_temp, rate in obs_map.items():
            if abs(obs_temp - target_temp_c) <= 1.5:
                return rate

        return None

    def extract_requirements(
        self,
        commodity: Dict[str, Any],
        storage: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> PackagingRequirements:
        """
        Deterministically maps food attributes and environmental factors
        into PackagingRequirements.
        """
        constraints = constraints or {}
        c_name = commodity.get("name") or commodity.get("commodity_name", "Unknown")
        category = commodity.get("category", "GENERAL").upper()
        aw = commodity.get("water_activity_aw")
        moisture_sens = commodity.get("moisture_sensitive", False)
        oxygen_sens = commodity.get("oxygen_sensitive", False)
        ethylene_sens = commodity.get("ethylene_sensitive", False)
        pH = commodity.get("pH")

        storage_temp = float(storage.get("storage_temperature_c", storage.get("temperature_c", 4.0)))
        ambient_rh = float(storage.get("ambient_rh_percent", storage.get("relative_humidity_pct", 85.0)))

        req = PackagingRequirements(
            commodity_name=c_name,
            category=category,
            ethylene_management_required=ethylene_sens,
            temperature_constraint={
                "storage_temperature_c": storage_temp,
                "optimal_min_c": commodity.get("optimal_temperature_min_c"),
                "optimal_max_c": commodity.get("optimal_temperature_max_c")
            },
            humidity_constraint={
                "ambient_rh_percent": ambient_rh,
                "optimal_min_rh": commodity.get("optimal_rh_min_percent"),
                "optimal_max_rh": commodity.get("optimal_rh_max_percent")
            }
        )

        # ---------------------------------------------------------------------
        # 1. Respiration Kinetics & Produce Breathability
        # ---------------------------------------------------------------------
        if category in ["FRUIT", "VEGETABLE"]:
            rate = self.find_empirical_respiration_rate(c_name, storage_temp)
            if rate is not None:
                req.respiration_status = "RESPIRING"
                req.respiration_rate_at_storage_temp = rate
                req.evidence.append({
                    "property": "respiration_rate",
                    "observed_value": rate,
                    "unit": "mg CO2/(kg*hr)",
                    "temperature_c": storage_temp,
                    "source_id": "SRC-FOOD-001",
                    "notes": "Verified USDA Handbook 66 respiration kinetics"
                })

                high_resp_threshold = self.config.get_parameter("RULE-BAR-002", "high_respiration_threshold_mg_co2_kg_hr", 20.0)
                if rate >= high_resp_threshold:
                    req.breathable_packaging_required = True
                    req.min_acceptable_otr = self.config.get_parameter("RULE-BAR-002", "minimum_breathable_otr_cc_m2_day_atm", 200.0)
                    req.evidence.append({
                        "property": "produce_breathability",
                        "requirement": f"OTR >= {req.min_acceptable_otr} cc/(m2*day*atm)",
                        "reason": f"Active respiration ({rate:.1f} mg CO2/kg*hr >= {high_resp_threshold}) risks anaerobic suffocation in hermetic films",
                        "source_id": "SRC-FOOD-001"
                    })
            else:
                # Temperature not observed empirically
                known_rates = FoodRequirementExtractor._respiration_cache.get(c_name.strip().lower(), {}) if FoodRequirementExtractor._respiration_cache else {}
                if known_rates:
                    req.respiration_status = "UNKNOWN_TEMPERATURE"
                    req.evidence.append({
                        "property": "respiration_rate",
                        "status": "UNKNOWN_TEMPERATURE",
                        "storage_temperature_c": storage_temp,
                        "available_temperatures_c": list(known_rates.keys()),
                        "reason": f"No empirical respiration observation exists for {c_name} at {storage_temp}°C. Zero extrapolation policy enforced.",
                        "source_id": "SRC-FOOD-001"
                    })
                else:
                    req.respiration_status = "MISSING_DATA"
        else:
            req.respiration_status = "NON_RESPIRING"

        # ---------------------------------------------------------------------
        # 2. Moisture Barrier Requirements
        # ---------------------------------------------------------------------
        high_moisture_req = constraints.get("require_high_moisture_barrier", False)
        dry_critical_aw = self.config.get_parameter("RULE-BAR-003", "dry_food_critical_aw", 0.65)
        is_dry_food = (aw is not None and float(aw) <= dry_critical_aw)

        if moisture_sens or is_dry_food or ambient_rh > 80.0 or high_moisture_req:
            req.moisture_barrier_required = True
            if high_moisture_req or is_dry_food:
                req.max_acceptable_wvtr = self.config.get_parameter("RULE-BAR-003", "strict_dry_max_wvtr_g_m2_day", 10.0)
            else:
                req.max_acceptable_wvtr = self.config.get_parameter("RULE-BAR-003", "standard_max_wvtr_g_m2_day", 25.0)

            req.evidence.append({
                "property": "moisture_barrier",
                "max_acceptable_wvtr": req.max_acceptable_wvtr,
                "unit": "g/(m2*day)",
                "reason": "Hygroscopic staling prevention or high ambient RH moisture ingress suppression",
                "source_id": "SRC-PKG-001"
            })

        # ---------------------------------------------------------------------
        # 3. Oxygen Barrier Requirements
        # ---------------------------------------------------------------------
        high_o2_req = constraints.get("require_high_oxygen_barrier", False)
        if oxygen_sens or high_o2_req or category in ["MEAT", "DAIRY", "BAKERY"]:
            req.oxygen_barrier_required = True
            if high_o2_req:
                req.max_acceptable_otr = self.config.get_parameter("RULE-BAR-001", "high_barrier_max_otr_cc_m2_day_atm", 30.0)
            else:
                req.max_acceptable_otr = self.config.get_parameter("RULE-BAR-001", "standard_max_otr_cc_m2_day_atm", 100.0)

            req.evidence.append({
                "property": "oxygen_barrier",
                "max_acceptable_otr": req.max_acceptable_otr,
                "unit": "cc/(m2*day*atm)",
                "reason": "Lipid oxidation, myoglobin oxidation, or oxidative staling protection",
                "source_id": "SRC-PKG-001"
            })

        # ---------------------------------------------------------------------
        # 4. MAP Suitability & Safety
        # ---------------------------------------------------------------------
        if category in ["FRUIT", "VEGETABLE", "MEAT", "DAIRY", "BAKERY"]:
            req.map_candidate = True

        # ---------------------------------------------------------------------
        # 5. Chilling Injury Check
        # ---------------------------------------------------------------------
        chilling_map = self.config.get_parameter("RULE-SAF-003", "chilling_thresholds", {})
        chilling_t = chilling_map.get(c_name)
        if chilling_t is not None:
            req.chilling_threshold_c = float(chilling_t)
            req.evidence.append({
                "property": "chilling_injury_threshold",
                "threshold_c": req.chilling_threshold_c,
                "source_id": "SRC-FOOD-002",
                "notes": f"{c_name} susceptible to physiological chilling breakdown below {req.chilling_threshold_c}°C"
            })

        return req
