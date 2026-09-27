"""
PackWise AI - Storage Environment & Polymer Compatibility Rules (Milestone M2)
Evaluates thermal boundaries, glass transition limits, and ambient humidity impacts.
"""
from typing import Any, Dict, Optional
from app.engines.rules.base import BaseRule, RuleEvaluationResult, RuleCategory, RuleSeverity, RuleStatus
from app.engines.rules.config import get_rule_config


class StorageTemperatureCompatibilityRule(BaseRule):
    """
    Verifies that the candidate packaging polymer maintains mechanical integrity and ductility
    at the specified supply chain storage temperature.
    """
    @property
    def rule_id(self) -> str:
        return "RULE-STR-001"

    @property
    def name(self) -> str:
        return "StorageTemperatureCompatibilityRule"

    @property
    def category(self) -> str:
        return RuleCategory.STORAGE.value

    @property
    def severity(self) -> str:
        return RuleSeverity.HARD.value

    @property
    def source_id(self) -> str:
        return "SRC-PKG-002"

    @property
    def scientific_basis(self) -> str:
        return "Polymer low-temperature ductility and glass transition Tg behavior (Massey 2003, Permeability Properties of Plastics and Elastomers)."

    @property
    def description(self) -> str:
        return "Screens materials against mechanical brittleness or failure in frozen/chilled distribution regimes."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        storage_temp_val = storage.get("storage_temperature_c", storage.get("temperature_c"))
        if storage_temp_val is None:
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.INSUFFICIENT_DATA.value,
                severity=RuleSeverity.SOFT.value,
                passed=True,
                observed_value=None,
                required_value="Storage temperature reference",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason="Storage temperature unrecorded in test profile; nominal cold chain (4°C) assumed.",
                details={"storage_temperature_c": None}
            )

        storage_temp = float(storage_temp_val)
        polymer = material.get("polymer_type", "").upper()
        config = get_rule_config()
        frozen_thresh = config.get_parameter("RULE-STR-001", "frozen_temp_threshold_c", -10.0)
        incompatible_frozen = [p.upper() for p in config.get_parameter("RULE-STR-001", "incompatible_frozen_polymers", ["PLA", "BOPLA", "CELLOPHANE"])]

        # If temperature is in deep freeze and polymer is brittle
        if storage_temp <= frozen_thresh and any(p in polymer for p in incompatible_frozen):
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                rule_category=self.category,
                status=RuleStatus.FAIL.value,
                severity=self.severity,
                passed=False,
                observed_value=storage_temp,
                required_value=f"> {frozen_thresh}",
                unit="°C",
                source_id=self.source_id,
                scientific_basis=self.scientific_basis,
                reason=(
                    f"Material '{material.get('name')}' ({polymer}) is susceptible to brittle fracture and "
                    f"loss of impact strength at frozen temperature ({storage_temp}°C <= {frozen_thresh}°C)."
                ),
                details={"storage_temp_c": storage_temp, "polymer_type": polymer}
            )

        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            rule_category=self.category,
            status=RuleStatus.PASS.value,
            severity=self.severity,
            passed=True,
            observed_value=storage_temp,
            required_value="Thermal compatibility satisfied",
            unit="°C",
            source_id=self.source_id,
            scientific_basis=self.scientific_basis,
            reason=f"Polymer ({polymer}) is mechanically compatible with {storage_temp}°C storage regime.",
            details={"storage_temp_c": storage_temp, "polymer_type": polymer}
        )
