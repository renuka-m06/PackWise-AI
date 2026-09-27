"""
PackWise AI - Material Compatibility Evaluator (Milestone M2)
Evaluates candidate packaging materials against empirical commodity and storage
constraints using strict rule priority and hard/soft constraint separation.
"""
from typing import Dict, Any, List, Optional
from app.engines.rules.base import BaseRule, RuleEvaluationResult, RuleStatus, RuleSeverity, RuleCategory
from app.engines.rules.safety_rules import (
    DataIntegrityRule,
    FoodContactCertificationRule,
    MAPPathogenSafetyRule,
    ChillingInjuryRule
)
from app.engines.rules.storage_rules import StorageTemperatureCompatibilityRule
from app.engines.rules.barrier_rules import (
    OxygenBarrierRule,
    ProduceBreathabilityRule,
    MoistureBarrierRule
)
from app.engines.rules.map_rules import MAPCompatibilityRule
from app.engines.rules.food_rules import PackagingRequirements


class MaterialCompatibilityEvaluator:
    """
    Evaluates individual packaging materials against strict scientific rules.
    Executes rules in priority order:
      1. DATA VALIDITY
      2. FOOD CONTACT / SAFETY
      3. STORAGE COMPATIBILITY
      4. CRITICAL BARRIER REQUIREMENTS
      5. MATERIAL COMPATIBILITY
      6. MAP COMPATIBILITY
      7. OPTIONAL PERFORMANCE PREFERENCES (Soft criteria)
    """
    def __init__(self, custom_rules: Optional[List[BaseRule]] = None):
        if custom_rules is not None:
            self.rules = custom_rules
        else:
            # Ordered strictly by priority
            self.rules = [
                DataIntegrityRule(),
                FoodContactCertificationRule(),
                MAPPathogenSafetyRule(),
                ChillingInjuryRule(),
                StorageTemperatureCompatibilityRule(),
                ProduceBreathabilityRule(),
                OxygenBarrierRule(),
                MoistureBarrierRule(),
                MAPCompatibilityRule(),
            ]

    def evaluate_material(
        self,
        commodity: Dict[str, Any],
        storage_condition: Dict[str, Any],
        material: Dict[str, Any],
        requirements: Optional[PackagingRequirements] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes deterministic rules against a single candidate material.
        Returns structured evaluation dictionary.
        """
        constraints = constraints or {}
        mat_id = str(material.get("id") or material.get("code") or material.get("name", "Unknown"))
        mat_code = str(material.get("code", "UNKNOWN"))
        mat_name = str(material.get("name", "Unknown Material"))

        checks: List[Dict[str, Any]] = []
        failed_rules: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []

        has_hard_failure = False
        has_insufficient_data = False

        for rule in self.rules:
            result: RuleEvaluationResult = rule.evaluate(
                commodity=commodity,
                material=material,
                storage=storage_condition,
                requirements=requirements
            )

            check_entry = {
                "rule_id": result.rule_id,
                "rule_name": result.rule_name,
                "rule_category": result.rule_category,
                "status": result.status,
                "severity": result.severity,
                "observed_value": result.observed_value,
                "required_value": result.required_value,
                "unit": result.unit,
                "source_id": result.source_id,
                "scientific_basis": result.scientific_basis,
                "reason": result.reason,
                "details": result.details
            }
            checks.append(check_entry)

            # Collect evidence
            if result.source_id and result.source_id != "DERIVED_ENGINEERING_RULE":
                evidence.append({
                    "rule_id": result.rule_id,
                    "source_id": result.source_id,
                    "scientific_basis": result.scientific_basis
                })

            # Check hard failure
            if result.status == RuleStatus.FAIL.value:
                if result.severity == RuleSeverity.HARD.value:
                    has_hard_failure = True
                    failed_rules.append(check_entry)
                else:
                    warnings.append(check_entry)

            # Check insufficient data on mandatory rules
            elif result.status == RuleStatus.INSUFFICIENT_DATA.value:
                if result.severity == RuleSeverity.HARD.value:
                    has_insufficient_data = True
                    failed_rules.append(check_entry)
                else:
                    warnings.append(check_entry)

        # ---------------------------------------------------------------------
        # Soft Criteria / Preferences (Do not eliminate material)
        # ---------------------------------------------------------------------
        # Biodegradability soft check if not strictly required
        prefer_bio = constraints.get("prefer_biodegradable", False)
        is_bio = material.get("is_biodegradable", False)
        if prefer_bio and not is_bio:
            warnings.append({
                "rule_id": "PREF-BIO-001",
                "rule_name": "BiodegradabilityPreference",
                "rule_category": RuleCategory.MATERIAL.value,
                "status": "NOT_PREFERRED",
                "severity": RuleSeverity.SOFT.value,
                "observed_value": False,
                "required_value": "Preference for biodegradable polymer",
                "source_id": "SRC-PKG-003",
                "reason": f"Material '{mat_name}' is non-biodegradable; penalized in sustainability scoring."
            })

        # Cost ceiling soft check
        max_cost = constraints.get("max_acceptable_cost_index")
        if max_cost is not None and material.get("cost_index_relative") is not None:
            cost_idx = float(material["cost_index_relative"])
            if cost_idx > float(max_cost):
                warnings.append({
                    "rule_id": "PREF-COST-001",
                    "rule_name": "CostCeilingPreference",
                    "rule_category": RuleCategory.MATERIAL.value,
                    "status": "NOT_PREFERRED",
                    "severity": RuleSeverity.SOFT.value,
                    "observed_value": cost_idx,
                    "required_value": f"<= {max_cost}",
                    "source_id": "DERIVED_ENGINEERING_RULE",
                    "reason": f"Material cost index ({cost_idx}) exceeds target preference ceiling ({max_cost})."
                })

        # Assign final status
        if has_hard_failure:
            status = "REJECTED"
        elif has_insufficient_data:
            status = "INSUFFICIENT_DATA"
        else:
            status = "ELIGIBLE"

        return {
            "material_id": mat_id,
            "material_code": mat_code,
            "material_name": mat_name,
            "status": status,
            "is_eligible": status == "ELIGIBLE",
            "checks": checks,
            "failed_rules": failed_rules,
            "warnings": warnings,
            "evidence": evidence
        }
