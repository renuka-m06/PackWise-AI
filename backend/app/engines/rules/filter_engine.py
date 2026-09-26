from typing import List, Dict, Any, Tuple
from app.engines.rules.base import BaseRule, RuleEvaluationResult
from app.engines.rules.barrier_rules import MoistureSensitivityRule, OxygenSensitivityRule
from app.engines.rules.safety_rules import FoodContactCertificationRule, BiodegradabilityConstraintRule


class RuleFilterEngine:
    """
    Coordinates rule evaluation to filter out ineligible packaging materials
    before machine learning prediction and TOPSIS multi-criteria ranking.
    """
    def __init__(self, rules: List[BaseRule] | None = None):
        if rules is None:
            self.rules: List[BaseRule] = [
                FoodContactCertificationRule(),
                MoistureSensitivityRule(),
                OxygenSensitivityRule(),
                BiodegradabilityConstraintRule(),
            ]
        else:
            self.rules = rules

    def screen_materials(
        self,
        commodity: Dict[str, Any],
        materials: List[Dict[str, Any]],
        storage: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[RuleEvaluationResult]]:
        """
        Runs all active rules on candidate materials.
        Returns:
            - passed_materials: List of materials passing all criteria
            - rejected_materials: List of materials failing one or more rules
            - audit_log: List of all evaluation results
        """
        passed_materials: List[Dict[str, Any]] = []
        rejected_materials: List[Dict[str, Any]] = []
        audit_log: List[RuleEvaluationResult] = []

        for material in materials:
            all_passed = True
            for rule in self.rules:
                result = rule.evaluate(commodity, material, storage)
                audit_log.append(result)
                if not result.passed:
                    all_passed = False
                    # Keep evaluating other rules for comprehensive audit or break
            
            if all_passed:
                passed_materials.append(material)
            else:
                rejected_materials.append(material)

        return passed_materials, rejected_materials, audit_log
