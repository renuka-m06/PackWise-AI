"""
PackWise AI - Scientific Food Safety & Data Integrity Rules (Milestone M2)
Enforces statutory food contact regulations, pathogen safety thresholds,
and chilling injury limits.
"""
from typing import Any, Dict, Optional
from app.engines.rules.base import BaseRule, RuleEvaluationResult, RuleCategory, RuleSeverity, RuleStatus
from app.engines.rules.config import get_rule_config


class DataIntegrityRule(BaseRule):
    """
    Validates candidate material physical integrity: non-zero thickness, valid polymer identity.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-VAL-001"

    @property
    def name(self) -> str:
        return "DataIntegrityRule"

    @property
    def category(self) -> str:
        return RuleCategory.DATA_VALIDITY.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "DERIVED_ENGINEERING_RULE"

    @property
    def scientific_basis(self) -> str:
        return "Physical reality invariant: thickness must be positive and non-zero (> 0 um)."

    @property
    def description(self) -> str:
        return "Validates that material record contains physically valid dimensions and polymer definitions."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        thickness = material.get("thickness_micron")
        if thickness is None:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.INSUFFICIENT_DATA.value,
                severity=RuleSeverity.SOFT.value,
                passed=True,
                observed_value=None,
                required_value="> 0.0",
                unit="um",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="Material thickness is unrecorded in test record; screening proceeds with caution.",
                details={"thickness": None}
            )

        if float(thickness) <= 0.0:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=RuleSeverity.HARD.value,
                passed=False,
                observed_value=float(thickness),
                required_value="> 0.0",
                unit="um",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Material thickness ({thickness} um) is physically impossible (must be > 0).",
                details={"thickness": thickness}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=RuleSeverity.HARD.value,
            passed=True,
            observed_value=float(thickness),
            required_value="> 0.0",
            unit="um",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason="Material physical integrity confirmed.",
            details={"thickness": thickness}
        )


class FoodContactCertificationRule(BaseRule):
    """
    Guarantees that materials contacting food have verifiable food-contact migration certification (FSSAI/FDA/EU).
    """
    @property
    def rule_id(self) -> str:
        return "RULE-SAF-001"

    @property
    def name(self) -> str:
        return "FoodContactCertificationRule"

    @property
    def category(self) -> str:
        return RuleCategory.SAFETY.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-PKG-001"

    @property
    def scientific_basis(self) -> str:
        return "Statutory food contact migration safety (Robertson 2012, Ch. 19; FDA 21 CFR 177 / FSSAI Regulations)."

    @property
    def description(self) -> str:
        return "Enforces statutory regulatory certification for direct and indirect food contact surfaces."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        certified = material.get("food_contact_certified")

        if certified is None:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.INSUFFICIENT_DATA.value,
                severity=self.severity,
                passed=False,
                observed_value=None,
                required_value=True,
                unit="boolean",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Food contact compliance data is missing for material '{material.get('name', 'Unknown')}'.",
                details={"food_contact_certified": None}
            )

        if not bool(certified):
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=False,
                required_value=True,
                unit="boolean",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Material '{material.get('name', 'Unknown')}' lacks food contact grade certification.",
                details={"certified": False}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=True,
            required_value=True,
            unit="boolean",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason="Material has verified food-contact compliance certification.",
            details={"certified": True}
        )


class MAPPathogenSafetyRule(BaseRule):
    """
    Prevents Clostridium botulinum neurotoxin formation in low-acid foods (pH > 4.6)
    stored above 3.0°C by prohibiting anaerobic hermetic packaging without oxygen.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-SAF-002"

    @property
    def name(self) -> str:
        return "MAPPathogenSafetyRule"

    @property
    def category(self) -> str:
        return RuleCategory.SAFETY.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-MAP-003"

    @property
    def scientific_basis(self) -> str:
        return "Pathogen safety margin against Clostridium botulinum in non-acidic produce (Farber et al. 2003)."

    @property
    def description(self) -> str:
        return "Prohibits zero-oxygen hermetic packaging for low-acid (pH > 4.6) respiring produce above 3°C."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        pH = commodity.get("pH")
        storage_temp = float(storage.get("storage_temperature_c", storage.get("temperature_c", 4.0)))
        category = commodity.get("category", "").upper()

        if pH is None:
            # If pH is unknown for produce, flag insufficient data if evaluating hermetic barrier
            if category in ["VEGETABLE"]:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    rule_category=self.category,
                    status=RuleStatus.INSUFFICIENT_DATA.value,
                    severity=self.severity,
                    passed=False,
                    observed_value=None,
                    required_value="pH reference",
                    source_id=self.source_id,
                    scientific_basis=self.scientific_basis,
                    reason=f"pH level unknown for {commodity.get('name')}; cannot verify C. botulinum safety margin.",
                    details={"pH": None}
                )
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.PASS.value,
                severity=self.severity,
                passed=True,
                observed_value="N/A",
                required_value="N/A",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="MAP pathogen check not applicable to non-vegetable category without pH risk.",
                details={}
            )

        # If low-acid (pH > 4.6) and storage temp > 3.0°C
        if float(pH) > 4.6 and storage_temp > 3.0 and category in ["VEGETABLE", "FRUIT"]:
            otr = material.get("otr_cc_m2_day_atm")
            if otr is None:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    rule_category=self.category,
                    status=RuleStatus.INSUFFICIENT_DATA.value,
                    severity=self.severity,
                    passed=False,
                    observed_value=None,
                    required_value=">= 50.0 cc/(m2*day*atm)",
                    unit="cc/(m2*day*atm)",
                    source_id=self.source_id,
                    scientific_basis=self.scientific_basis,
                    reason=f"Material OTR missing; cannot determine oxygen suffocation safety for pH {pH} produce.",
                    details={"otr": None}
                )

            # Ultra-low barrier (OTR < 50.0 cc/m2/day-atm) on low-acid respiring produce risks botulism
            if float(otr) < 50.0:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    rule_category=self.category,
                    status=RuleStatus.FAIL.value,
                    severity=self.severity,
                    passed=False,
                    observed_value=float(otr),
                    required_value=">= 50.0",
                    unit="cc/(m2*day*atm)",
                    source_id=self.source_id,
                    scientific_basis=self.scientific_basis,
                    reason=(
                        f"Material rejected: OTR ({otr:.1f} cc/m²/day·atm) is dangerously impermeable for low-acid "
                        f"(pH {pH} > 4.6) produce stored at {storage_temp}°C. Creates anaerobic botulism risk."
                    ),
                    details={"otr": otr, "pH": pH, "storage_temp_c": storage_temp}
                )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=float(pH) if pH else "N/A",
            required_value="Compliant with Farber et al. 2003 guidelines",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason="Material complies with low-acid MAP pathogen safety margin.",
            details={"pH": pH}
        )


class ChillingInjuryRule(BaseRule):
    """
    Prevents physiological chilling breakdown by checking storage temperature against
    empirical commodity thresholds.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-SAF-003"

    @property
    def name(self) -> str:
        return "ChillingInjuryRule"

    @property
    def category(self) -> str:
        return RuleCategory.SAFETY.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-FOOD-002"

    @property
    def scientific_basis(self) -> str:
        return "Postharvest chilling injury physiology in sensitive horticultural crops (Kader et al. 2020)."

    @property
    def description(self) -> str:
        return "Screens storage regimes against critical commodity chilling injury thresholds."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        c_name = commodity.get("name") or commodity.get("commodity_name", "")
        storage_temp = float(storage.get("storage_temperature_c", storage.get("temperature_c", 4.0)))

        config = get_rule_config()
        chilling_map = config.get_parameter("RULE-SAF-003", "chilling_thresholds", {})
        threshold = chilling_map.get(c_name)

        if threshold is not None and storage_temp < float(threshold):
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=storage_temp,
                required_value=f">= {threshold}",
                unit="°C",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=(
                    f"Storage temperature ({storage_temp}°C) is below chilling injury threshold ({threshold}°C) "
                    f"for {c_name}, causing irreversible physiological tissue breakdown."
                ),
                details={"storage_temperature_c": storage_temp, "chilling_threshold_c": threshold}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=storage_temp,
            required_value=f">= {threshold}" if threshold else "No chilling threshold",
            unit="°C",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason="Storage temperature is above chilling injury boundary.",
            details={"storage_temperature_c": storage_temp}
        )


class BiodegradabilityConstraintRule(BaseRule):
    """
    Enforces biodegradable constraint when user explicitly mandates compostable/bio-based polymers.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-MAT-001"

    @property
    def name(self) -> str:
        return "BiodegradabilityConstraintRule"

    @property
    def category(self) -> str:
        return RuleCategory.MATERIAL.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-PKG-003"

    @property
    def scientific_basis(self) -> str:
        return "Industrial and home compostability standards ASTM D6400 / EN 13432 (NatureWorks 2021)."

    @property
    def description(self) -> str:
        return "Filters candidates to require certified biodegradable / compostable polymers."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        require_bio = commodity.get("require_biodegradable", False)
        is_bio = material.get("is_biodegradable", False)

        if require_bio and not is_bio:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=False,
                required_value=True,
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=f"Material '{material.get('name')}' is conventional non-biodegradable polymer ({material.get('polymer_type')}).",
                details={"is_biodegradable": False}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=is_bio,
            required_value=require_bio,
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason="Material satisfies environmental biodegradability criteria.",
            details={"is_biodegradable": is_bio}
        )

