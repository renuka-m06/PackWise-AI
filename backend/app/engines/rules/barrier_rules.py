from typing import Any, Dict
from app.engines.rules.base import BaseRule, RuleEvaluationResult


class MoistureSensitivityRule(BaseRule):
    """
    Screens materials to ensure adequate moisture barrier (WVTR) when commodity is moisture-sensitive
    or when ambient relative humidity is high (RH > 80%).
    """
    @property
    def name(self) -> str:
        return "MoistureSensitivityBarrierRule"

    @property
    def description(self) -> str:
        return "Ensures film Water Vapor Transmission Rate (WVTR) prevents dehydration or moisture condensation."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> RuleEvaluationResult:
        is_sensitive = commodity.get("moisture_sensitive", False)
        ambient_rh = storage.get("ambient_rh_percent", 50.0)
        wvtr = material.get("wvtr_g_m2_day", 100.0)

        # If moisture sensitive or very high RH, maximum acceptable WVTR is 15.0 g/m²/day
        if (is_sensitive or ambient_rh > 80.0) and wvtr > 25.0:
            return RuleEvaluationResult(
                rule_name=self.name,
                passed=False,
                explanation=f"Material WVTR ({wvtr:.1f} g/m²/day) exceeds threshold (25.0 g/m²/day) for high humidity/moisture-sensitive commodity.",
                details={"wvtr": wvtr, "threshold": 25.0}
            )

        return RuleEvaluationResult(
            rule_name=self.name,
            passed=True,
            explanation=f"Material WVTR ({wvtr:.1f} g/m²/day) meets moisture barrier safety threshold.",
            details={"wvtr": wvtr}
        )


class OxygenSensitivityRule(BaseRule):
    """
    Screens materials to ensure adequate oxygen barrier (OTR) when commodity is prone to lipid oxidation,
    enzymatic browning, or oxidative rancidity.
    """
    @property
    def name(self) -> str:
        return "OxygenSensitivityBarrierRule"

    @property
    def description(self) -> str:
        return "Ensures film Oxygen Transmission Rate (OTR) protects against oxidative degradation."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> RuleEvaluationResult:
        is_sensitive = commodity.get("oxygen_sensitive", False)
        otr = material.get("otr_cc_m2_day_atm", 2000.0)

        if is_sensitive and otr > 50.0:
            return RuleEvaluationResult(
                rule_name=self.name,
                passed=False,
                explanation=f"Material OTR ({otr:.1f} cc/m²/day-atm) exceeds maximum limit (50.0 cc/m²/day-atm) for oxygen-sensitive produce.",
                details={"otr": otr, "threshold": 50.0}
            )

        return RuleEvaluationResult(
            rule_name=self.name,
            passed=True,
            explanation=f"Material OTR ({otr:.1f} cc/m²/day-atm) is compliant with oxygen tolerance requirements.",
            details={"otr": otr}
        )
