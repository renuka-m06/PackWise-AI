"""
PackWise AI - Scientific Rule Screening Engine (Milestone M2)
Coordinates deterministic rule evaluation across candidate packaging materials.
Enforces strict rule priority, hard constraint elimination, and zero-fabrication policies.
"""
from typing import List, Dict, Any, Tuple, Optional
from app.engines.rules.base import BaseRule, RuleEvaluationResult
from app.engines.rules.food_rules import FoodRequirementExtractor, PackagingRequirements
from app.engines.rules.compatibility import MaterialCompatibilityEvaluator
from app.engines.rules.explanations import ExplanationGenerator

RULE_ENGINE_VERSION = "m2.0.0"


class RuleFilterEngine:
    """
    Coordinates rule evaluation to filter out ineligible packaging materials
    before TOPSIS multi-criteria ranking and machine learning prediction.
    """
    def __init__(self, rules: Optional[List[BaseRule]] = None):
        self.version = RULE_ENGINE_VERSION
        self.compatibility_evaluator = MaterialCompatibilityEvaluator(custom_rules=rules)
        self.requirement_extractor = FoodRequirementExtractor()
        self.rules: List[BaseRule] = self.compatibility_evaluator.rules

    def derive_requirements(
        self,
        commodity: Dict[str, Any],
        storage: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> PackagingRequirements:
        """Derives structured packaging requirements from food and logistics parameters."""
        return self.requirement_extractor.extract_requirements(commodity, storage, constraints)

    def screen_materials(
        self,
        commodity: Dict[str, Any],
        materials: List[Dict[str, Any]],
        storage: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[RuleEvaluationResult]]:
        """
        Runs priority rules on candidate materials.
        Returns:
            - passed_materials: List of materials passing all hard constraints (status == 'ELIGIBLE')
            - rejected_materials: List of materials failing one or more hard constraints
            - audit_log: List of all individual RuleEvaluationResult objects
        """
        requirements = self.derive_requirements(commodity, storage, constraints)

        passed_materials: List[Dict[str, Any]] = []
        rejected_materials: List[Dict[str, Any]] = []
        audit_log: List[RuleEvaluationResult] = []

        for material in materials:
            eval_res = self.compatibility_evaluator.evaluate_material(
                commodity=commodity,
                storage_condition=storage,
                material=material,
                requirements=requirements,
                constraints=constraints
            )

            # Convert check dictionaries back into RuleEvaluationResult for backward-compatible audit_log
            for check in eval_res["checks"]:
                audit_log.append(RuleEvaluationResult(
                    rule_id=check["rule_id"],
                    rule_name=check["rule_name"],
                    rule_category=check["rule_category"],
                    status=check["status"],
                    severity=check["severity"],
                    passed=(check["status"] == "PASS"),
                    observed_value=check["observed_value"],
                    required_value=check["required_value"],
                    unit=check.get("unit"),
                    source_id=check.get("source_id", "DERIVED_ENGINEERING_RULE"),
                    scientific_basis=check.get("scientific_basis", ""),
                    reason=check.get("reason", ""),
                    explanation=check.get("reason", ""),
                    details=check.get("details", {})
                ))

            if eval_res["status"] == "ELIGIBLE":
                # Annotate material with evaluation summary and evidence
                enriched_mat = dict(material)
                enriched_mat["_evaluation"] = eval_res
                passed_materials.append(enriched_mat)
            else:
                enriched_mat = dict(material)
                enriched_mat["_evaluation"] = eval_res
                rejected_materials.append(enriched_mat)

        return passed_materials, rejected_materials, audit_log

    def screen_materials_detailed(
        self,
        commodity: Dict[str, Any],
        materials: List[Dict[str, Any]],
        storage: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Returns full structured evaluation payload including requirements, eligible materials,
        rejected materials, and comprehensive evidence graphs.
        """
        requirements = self.derive_requirements(commodity, storage, constraints)
        evaluations: List[Dict[str, Any]] = []
        eligible: List[Dict[str, Any]] = []
        rejected: List[Dict[str, Any]] = []

        for material in materials:
            eval_res = self.compatibility_evaluator.evaluate_material(
                commodity=commodity,
                storage_condition=storage,
                material=material,
                requirements=requirements,
                constraints=constraints
            )
            explanation = ExplanationGenerator.generate_candidate_explanation(eval_res)
            eval_res["explanation"] = explanation
            eval_res["evidence_graph"] = ExplanationGenerator.build_evidence_graph(
                commodity, storage, requirements, eval_res
            )
            evaluations.append(eval_res)

            if eval_res["status"] == "ELIGIBLE":
                eligible.append(material)
            else:
                rejected.append(material)

        return {
            "engine_version": self.version,
            "requirements": requirements,
            "total_candidates": len(materials),
            "eligible_count": len(eligible),
            "rejected_count": len(rejected),
            "eligible_materials": eligible,
            "rejected_materials": rejected,
            "evaluations": evaluations
        }
