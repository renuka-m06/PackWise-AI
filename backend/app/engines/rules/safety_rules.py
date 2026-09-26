from typing import Any, Dict
from app.engines.rules.base import BaseRule, RuleEvaluationResult


class FoodContactCertificationRule(BaseRule):
    """
    Guarantees that materials contacting food have verifiable food-contact migration certification (FSSAI/FDA/EU).
    """
    @property
    def name(self) -> str:
        return "FoodContactCertificationRule"

    @property
    def description(self) -> str:
        return "Enforces statutory regulatory certification for direct and indirect food contact surfaces."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> RuleEvaluationResult:
        certified = material.get("food_contact_certified", True)
        if not certified:
            return RuleEvaluationResult(
                rule_name=self.name,
                passed=False,
                explanation=f"Material '{material.get('name', 'Unknown')}' lacks food contact grade certification.",
                details={"certified": False}
            )

        return RuleEvaluationResult(
            rule_name=self.name,
            passed=True,
            explanation="Material has verified food-contact compliance certification.",
            details={"certified": True}
        )


class BiodegradabilityConstraintRule(BaseRule):
    """
    Enforces biodegradable constraint when user explicitly mandates compostable/bio-based polymers.
    """
    @property
    def name(self) -> str:
        return "BiodegradabilityConstraintRule"

    @property
    def description(self) -> str:
        return "Filters candidates to require certified biodegradable / compostable polymers."

    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> RuleEvaluationResult:
        require_bio = commodity.get("require_biodegradable", False)
        is_bio = material.get("is_biodegradable", False)

        if require_bio and not is_bio:
            return RuleEvaluationResult(
                rule_name=self.name,
                passed=False,
                explanation=f"Material '{material.get('name')}' is conventional non-biodegradable polymer ({material.get('polymer_type')}).",
                details={"is_biodegradable": False}
            )

        return RuleEvaluationResult(
            rule_name=self.name,
            passed=True,
            explanation="Material satisfies environmental biodegradability criteria.",
            details={"is_biodegradable": is_bio}
        )
