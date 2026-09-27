"""
PackWise AI - Scientific Barrier Rules (Milestone M2)
Evaluates Oxygen Transmission Rate (OTR, ASTM D3985 at 23°C/0% RH)
and Water Vapor Transmission Rate (WVTR, ASTM F1249 at 37.8°C/90% RH).
"""
from typing import Any, Dict, Optional
from app.engines.rules.base import BaseRule, RuleEvaluationResult, RuleCategory, RuleSeverity, RuleStatus
from app.engines.rules.config import get_rule_config


class OxygenBarrierRule(BaseRule):
    """
    Screens materials to ensure adequate oxygen barrier (OTR under ASTM D3985)
    when commodity is oxygen sensitive or high oxygen barrier is mandated.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-BAR-001"

    @property
    def name(self) -> str:
        return "OxygenBarrierRule"

    @property
    def category(self) -> str:
        return RuleCategory.BARRIER.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-PKG-001"

    @property
    def scientific_basis(self) -> str:
        return "Gas permeation through polymer films under ASTM D3985 at 23°C, 0% RH (Robertson 2012, Food Packaging Principles and Practice)."

    @property
    def description(self) -> str:
        return "Ensures film Oxygen Transmission Rate (OTR) satisfies preservation limits for oxygen-sensitive foods."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        is_sensitive = commodity.get("oxygen_sensitive", False)
        category = commodity.get("category", "").upper()
        high_o2_req = commodity.get("require_high_oxygen_barrier", False)
        if requirements:
            is_sensitive = is_sensitive or requirements.oxygen_barrier_required
            high_o2_req = high_o2_req or requirements.high_barrier_required

        # If commodity does not require oxygen barrier
        if not is_sensitive and not high_o2_req and category not in ["MEAT", "DAIRY", "BAKERY"]:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.PASS.value,
                severity=self.severity,
                passed=True,
                observed_value="Not constrained",
                required_value="Unrestricted",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="Commodity is not oxygen-sensitive; oxygen barrier constraint waived.",
                details={}
            )

        otr_val = material.get("otr_cc_m2_day_atm")
        if otr_val is None:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.INSUFFICIENT_DATA.value,
                severity=self.severity,
                passed=False,
                observed_value=None,
                required_value="OTR measurement under ASTM D3985",
                unit="cc/(m2*day*atm)",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Material '{material.get('name')}' lacks verified OTR measurement data under ASTM D3985.",
                details={"otr": None}
            )

        otr = float(otr_val)
        config = get_rule_config()
        if high_o2_req:
            max_limit = config.get_parameter("RULE-BAR-001", "high_barrier_max_otr_cc_m2_day_atm", 30.0)
        else:
            # Check if custom requirement threshold exists or default 50.0 / 100.0
            if requirements and requirements.max_acceptable_otr:
                max_limit = requirements.max_acceptable_otr
            else:
                max_limit = 50.0  # Strict baseline for oxygen sensitive items

        if otr > max_limit:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=otr,
                required_value=f"<= {max_limit}",
                unit="cc/(m2*day*atm)",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=(
                    f"Material rejected: OTR ({otr:.1f} cc/(m²·day·atm)) exceeds maximum permitted limit "
                    f"({max_limit:.1f} cc/(m²·day·atm)) under ASTM D3985 test conditions (23°C, 0% RH) "
                    f"for oxygen-sensitive produce."
                ),
                details={"otr": otr, "threshold": max_limit, "test_method": "ASTM D3985"}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=otr,
            required_value=f"<= {max_limit}",
            unit="cc/(m2*day*atm)",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason=f"Material OTR ({otr:.1f} cc/(m²·day·atm)) satisfies oxygen barrier requirement under ASTM D3985.",
            details={"otr": otr, "threshold": max_limit, "test_method": "ASTM D3985"}
        )


class ProduceBreathabilityRule(BaseRule):
    """
    Prevents anaerobic suffocation, tissue breakdown, and off-flavor generation in high-respiring
    produce by ensuring packaging film is sufficiently permeable (or microperforated).
    """
    @property
    def rule_id(self) -> str:
        return "RULE-BAR-002"

    @property
    def name(self) -> str:
        return "ProduceBreathabilityRule"

    @property
    def category(self) -> str:
        return RuleCategory.BARRIER.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-FOOD-001"

    @property
    def scientific_basis(self) -> str:
        return "Respiration kinetics and anaerobic threshold limits in active produce (Gross et al. 2016, USDA Handbook 66)."

    @property
    def description(self) -> str:
        return "Ensures high-respiring produce is not hermetically sealed in impermeable barrier films without breathability."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        is_respiring = False
        rate = None
        c_name = commodity.get("name") or commodity.get("commodity_name", "Produce")

        if requirements:
            is_respiring = requirements.breathable_packaging_required
            rate = requirements.respiration_rate_at_storage_temp

        if not is_respiring:
            # Check respiration rate if present in commodity
            resp_val = commodity.get("respiration_rate_mg_co2_kg_hr")
            if resp_val and float(resp_val) >= 20.0:
                is_respiring = True
                rate = float(resp_val)

        if not is_respiring:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.PASS.value,
                severity=self.severity,
                passed=True,
                observed_value="Non-respiring or low respiration",
                required_value="N/A",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="Produce breathability constraint not required.",
                details={}
            )

        otr_val = material.get("otr_cc_m2_day_atm")
        if otr_val is None:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.INSUFFICIENT_DATA.value,
                severity=self.severity,
                passed=False,
                observed_value=None,
                required_value="OTR data required",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Material '{material.get('name')}' lacks OTR data; breathability cannot be evaluated.",
                details={"otr": None}
            )

        otr = float(otr_val)
        config = get_rule_config()
        impermeable_ceiling = config.get_parameter("RULE-BAR-002", "impermeable_ceiling_otr_cc_m2_day_atm", 50.0)

        # If film is impermeable (< 50 cc/m2/day-atm, e.g. EVOH or high-barrier PET)
        if otr < impermeable_ceiling:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=otr,
                required_value=f">= {impermeable_ceiling}",
                unit="cc/(m2*day*atm)",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=(
                    f"Material rejected: OTR ({otr:.1f} cc/(m²·day·atm)) is impermeable. "
                    f"Active respiring produce ({c_name}, R = {rate or 'High'} mg CO2/(kg·hr)) "
                    f"will suffocate rapidly, triggering anaerobic fermentation and off-odors (Gross et al. 2016)."
                ),
                details={"otr": otr, "impermeable_ceiling": impermeable_ceiling, "respiration_rate": rate}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=otr,
            required_value=f">= {impermeable_ceiling}",
            unit="cc/(m2*day*atm)",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason=f"Material OTR ({otr:.1f} cc/(m²·day·atm)) provides sufficient gas transmission for respiring produce.",
            details={"otr": otr}
        )


class MoistureBarrierRule(BaseRule):
    """
    Screens materials to ensure adequate moisture barrier (WVTR under ASTM F1249)
    when commodity is moisture-sensitive, dry, or stored in high humidity (RH > 80%).
    """
    @property
    def rule_id(self) -> str:
        return "RULE-BAR-003"

    @property
    def name(self) -> str:
        return "MoistureBarrierRule"

    @property
    def category(self) -> str:
        return RuleCategory.BARRIER.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-PKG-001"

    @property
    def scientific_basis(self) -> str:
        return "Water vapor permeation through polymer films under ASTM F1249 at 37.8°C, 90% RH (Robertson 2012; Rockland & Beuchat 1987)."

    @property
    def description(self) -> str:
        return "Ensures film Water Vapor Transmission Rate (WVTR) prevents dehydration, condensation, or staling."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        is_sensitive = commodity.get("moisture_sensitive", False)
        ambient_rh = float(storage.get("ambient_rh_percent", storage.get("relative_humidity_pct", 50.0)))
        aw = commodity.get("water_activity_aw")
        high_moisture_req = commodity.get("require_high_moisture_barrier", False)

        if requirements:
            is_sensitive = is_sensitive or requirements.moisture_barrier_required

        config = get_rule_config()
        dry_aw_thresh = config.get_parameter("RULE-BAR-003", "dry_food_critical_aw", 0.65)
        is_dry_food = (aw is not None and float(aw) <= dry_aw_thresh)

        # If not sensitive, not dry, and ambient RH is normal
        if not is_sensitive and not is_dry_food and ambient_rh <= 80.0 and not high_moisture_req:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.PASS.value,
                severity=self.severity,
                passed=True,
                observed_value="Not constrained",
                required_value="Unrestricted",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="Commodity is not moisture-sensitive under moderate ambient humidity.",
                details={}
            )

        wvtr_val = material.get("wvtr_g_m2_day")
        if wvtr_val is None:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.INSUFFICIENT_DATA.value,
                severity=self.severity,
                passed=False,
                observed_value=None,
                required_value="WVTR measurement under ASTM F1249",
                unit="g/(m2*day)",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Material '{material.get('name')}' lacks verified WVTR measurement data under ASTM F1249.",
                details={"wvtr": None}
            )

        wvtr = float(wvtr_val)
        if high_moisture_req or is_dry_food:
            max_limit = config.get_parameter("RULE-BAR-003", "strict_dry_max_wvtr_g_m2_day", 10.0)
        else:
            max_limit = config.get_parameter("RULE-BAR-003", "standard_max_wvtr_g_m2_day", 25.0)

        if wvtr > max_limit:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=wvtr,
                required_value=f"<= {max_limit}",
                unit="g/(m2*day)",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=(
                    f"Material rejected: WVTR ({wvtr:.1f} g/m²/day) exceeds threshold ({max_limit:.1f} g/m²/day) "
                    f"under ASTM F1249 test conditions (37.8°C, 90% RH) for high humidity/moisture-sensitive commodity."
                ),
                details={"wvtr": wvtr, "threshold": max_limit, "test_method": "ASTM F1249"}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=wvtr,
            required_value=f"<= {max_limit}",
            unit="g/(m2*day)",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason=f"Material WVTR ({wvtr:.1f} g/m²/day) satisfies moisture barrier safety threshold under ASTM F1249.",
            details={"wvtr": wvtr, "threshold": max_limit, "test_method": "ASTM F1249"}
        )


# Aliases for backward compatibility with M0 test suite
MoistureSensitivityRule = MoistureBarrierRule
OxygenSensitivityRule = OxygenBarrierRule
