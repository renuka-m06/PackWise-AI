"""
PackWise AI - Modified Atmosphere Packaging (MAP) Rules (Milestone M2)
Evaluates gas balance, empirical headspace selection, and barrier compatibility.
Never fabricates MAP gas compositions.
"""
from typing import Any, Dict, List, Optional, Tuple
import os
import csv
from app.engines.rules.base import BaseRule, RuleEvaluationResult, RuleCategory, RuleSeverity, RuleStatus
from app.engines.rules.config import get_rule_config


class MAPCompatibilityRule(BaseRule):
    """
    Evaluates gas sum integrity and barrier retention for Modified Atmosphere Packaging.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-MAP-001"

    @property
    def name(self) -> str:
        return "MAPCompatibilityRule"

    @property
    def category(self) -> str:
        return RuleCategory.MAP.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-MAP-001"

    @property
    def scientific_basis(self) -> str:
        return "Equilibrium modified atmosphere formulation validity (Gorris & Peppelenbos 1992; Farber et al. 2003)."

    @property
    def description(self) -> str:
        return "Verifies MAP gas sum integrity (100% +- 1.5%) and barrier retention for modified headspaces."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        map_config = commodity.get("map_composition") or storage.get("map_composition")

        # If MAP is not configured for this evaluation, pass conditionally
        if not map_config:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.PASS.value,
                severity=self.severity,
                passed=True,
                observed_value="Not requested",
                required_value="N/A",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="MAP packaging not active for this evaluation.",
                details={}
            )

        o2 = float(map_config.get("oxygen_pct", 0.0))
        co2 = float(map_config.get("carbon_dioxide_pct", 0.0))
        n2 = float(map_config.get("nitrogen_pct", 0.0))
        total_gas = o2 + co2 + n2

        config = get_rule_config()
        tolerance = config.get_parameter("RULE-MAP-001", "gas_sum_tolerance_pct", 1.5)

        # 1. Physical gas sum validation
        if abs(total_gas - 100.0) > tolerance:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=total_gas,
                required_value=f"100.0% +- {tolerance}%",
                unit="%",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"MAP gas components ({o2}% O2 + {co2}% CO2 + {n2}% N2 = {total_gas}%) violate physical gas balance (must sum to 100% +- {tolerance}%).",
                details={"total_gas_pct": total_gas}
            )

        # 2. High CO2 barrier retention
        high_co2_thresh = config.get_parameter("RULE-MAP-001", "high_co2_threshold_pct", 15.0)
        max_otr_map = config.get_parameter("RULE-MAP-001", "max_otr_for_high_co2_map", 150.0)
        otr_val = material.get("otr_cc_m2_day_atm")

        if co2 >= high_co2_thresh:
            if otr_val is None:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    rule_category=self.category,
                    status=RuleStatus.INSUFFICIENT_DATA.value,
                    severity=self.severity,
                    passed=False,
                    observed_value=None,
                    required_value=f"<= {max_otr_map} cc/(m2*day*atm)",
                    unit="cc/(m2*day*atm)",
                    source_id=self.source_id,
                    scientific_basis=self.scientific_basis,
                    reason=f"Material lacks OTR data; cannot verify retention of high-CO2 MAP ({co2}% CO2).",
                    details={"otr": None}
                )

            otr = float(otr_val)
            if otr > max_otr_map:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    rule_category=self.category,
                    status=RuleStatus.FAIL.value,
                    severity=self.severity,
                    passed=False,
                    observed_value=otr,
                    required_value=f"<= {max_otr_map}",
                    unit="cc/(m2*day*atm)",
                    source_id=self.source_id,
                    scientific_basis=self.scientific_basis,
                    reason=(
                        f"Material rejected: OTR ({otr:.1f} cc/m²/day·atm) is too porous to maintain high-CO2 "
                        f"modified atmosphere ({co2}% CO2). Requires barrier film with OTR <= {max_otr_map} cc/(m²·day·atm)."
                    ),
                    details={"otr": otr, "co2_pct": co2, "max_otr": max_otr_map}
                )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=f"O2: {o2}%, CO2: {co2}%, N2: {n2}%",
            required_value="Verified MAP balance",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason="MAP gas formulation and film barrier compatibility verified.",
            details={"total_gas_pct": total_gas, "co2_pct": co2}
        )


class EmpiricalMAPSelector:
    """
    Selects empirical MAP formulations strictly from verified M1 datasets.
    If no empirical formulation matches the food category or commodity,
    returns MAP_STATUS = INSUFFICIENT_DATA rather than guessing.
    """
    _cached_map: Optional[List[Dict[str, Any]]] = None

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
            "data", "processed"
        )
        self._load_map_data()

    def _load_map_data(self):
        if EmpiricalMAPSelector._cached_map is not None:
            return

        compositions: List[Dict[str, Any]] = []
        csv_path = os.path.join(self.data_dir, "map_compositions.csv")
        if os.path.exists(csv_path):
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        compositions.append({
                            "composition_name": row["composition_name"],
                            "food_category": row["food_category"].upper(),
                            "oxygen_pct": float(row["oxygen_pct"]),
                            "carbon_dioxide_pct": float(row["carbon_dioxide_pct"]),
                            "nitrogen_pct": float(row["nitrogen_pct"]),
                            "recommended_temp_min_c": float(row["recommended_temp_min_c"]),
                            "recommended_temp_max_c": float(row["recommended_temp_max_c"]),
                            "packaging_context": row["packaging_context"],
                            "source_id": row["source_id"],
                            "source_reference": row["source_reference"]
                        })
            except Exception:
                pass
        EmpiricalMAPSelector._cached_map = compositions

    def select_candidate_map(
        self,
        commodity_name: str,
        category: str,
        storage_temp_c: float
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Returns:
            (matched_map_dict, status)
            status is 'VERIFIED' or 'INSUFFICIENT_DATA'
        """
        if not EmpiricalMAPSelector._cached_map:
            return None, "INSUFFICIENT_DATA"

        category = category.upper()
        # 1. Look for specific commodity keyword match in packaging_context or composition_name
        for m in EmpiricalMAPSelector._cached_map:
            if commodity_name.lower() in m["packaging_context"].lower() or commodity_name.lower() in m["composition_name"].lower():
                if m["recommended_temp_min_c"] <= storage_temp_c <= m["recommended_temp_max_c"] + 2.0:
                    return m, "VERIFIED"

        # 2. Look for category match within temperature envelope
        for m in EmpiricalMAPSelector._cached_map:
            if m["food_category"] == category:
                if m["recommended_temp_min_c"] <= storage_temp_c <= m["recommended_temp_max_c"] + 2.0:
                    return m, "VERIFIED"

        # Strict: Do NOT fabricate a MAP composition
        return None, "INSUFFICIENT_DATA"
