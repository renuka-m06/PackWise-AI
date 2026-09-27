"""
PackWise AI - End-to-End Recommendation Pipeline Orchestrator (Milestone M4)
Executes the authoritative scientific decision pipeline:
  REQUEST -> FOOD PROFILE -> STORAGE PROFILE -> PACKAGING REQUIREMENTS
  -> SCIENTIFIC RULE SCREENING -> HARD CONSTRAINT FILTERING
  -> TOPSIS MCDM RANKING (Eligible candidates only)
  -> PRIMARY RECOMMENDATION + ALTERNATIVES
  -> EVIDENCE GRAPH & EXPLANATION -> ML STATUS DISCLOSURE
"""
import uuid
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from app.schemas.recommendation import (
    RecommendationRequest, 
    RecommendationResponse,
    RuleFilterResult,
    MaterialScoreResponse
)
from app.schemas.material import PackagingMaterialResponse
from app.schemas.map_composition import MAPCompositionResponse
from app.engines.rules.filter_engine import RuleFilterEngine, RULE_ENGINE_VERSION
from app.engines.rules.food_rules import FoodRequirementExtractor
from app.engines.rules.map_rules import EmpiricalMAPSelector
from app.engines.rules.explanations import ExplanationGenerator
from app.engines.ranking.topsis import TOPSISDecisionEngine
from app.db.empirical_data import (
    get_verified_commodity,
    get_verified_materials
)


class RecommendationOrchestrator:
    """
    Authoritative recommendation orchestrator for PackWise AI (Milestone M4).
    Synthesizes empirical data resolution, deterministic rule screening,
    MCDM TOPSIS ranking, explainability, evidence graphs, and ML status reporting.
    """
    DATASET_VERSION = "1.0.0-m3"

    def __init__(self):
        self.rule_filter_engine = RuleFilterEngine()
        self.ranking_engine = TOPSISDecisionEngine()
        self.map_selector = EmpiricalMAPSelector()
        self.requirement_extractor = FoodRequirementExtractor()

    def process_recommendation_request(
        self, 
        request: RecommendationRequest,
        request_id: Optional[str] = None
    ) -> RecommendationResponse:
        request_id = request_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # ---------------------------------------------------------------------
        # 1. Resolve Food Profile from Verified Empirical Data (Section 4)
        # ---------------------------------------------------------------------
        commodity = get_verified_commodity(request.commodity_name)

        if not commodity:
            # Unverified commodity fallback: enforce strict anti-fabrication standard
            return RecommendationResponse(
                request_id=request_id,
                timestamp=now,
                status="PENDING_ENGINES",
                rule_engine_status="NOT_RUN",
                ml_status="INSUFFICIENT_VERIFIED_DATA",
                topsis_status="NOT_RUN",
                recommendation_status="DISARMED_UNVERIFIED",
                message=(
                    f"Commodity '{request.commodity_name}' was not found in the verified empirical repository. "
                    "In strict accordance with the anti-fabrication policy, recommendation engines remain "
                    "disarmed for unverified commodities. Zero synthetic or guessed parameters allowed."
                ),
                recommended_material=None,
                primary_recommendation=None,
                alternative_materials=[],
                suggested_map=None,
                candidate_rankings=[],
                applied_rules=[
                    RuleFilterResult(
                        rule_name="M0ContractValidationRule",
                        passed=True,
                        explanation=f"Commodity '{request.commodity_name}' parameters validated against Pydantic schema."
                    )
                ],
                evidence_graph=[],
                explanation="To execute recommendations, choose a verified commodity from the catalog (e.g., Strawberry, Broccoli, Apple, Tomato, Raw Beef, Cheddar Cheese).",
                dataset_version=self.DATASET_VERSION,
                rule_engine_version=RULE_ENGINE_VERSION,
                topsis_configuration_version=TOPSISDecisionEngine.CONFIG_VERSION,
                ml_model_version=None,
                audit_metadata={"unverified_commodity": request.commodity_name}
            )

        # ---------------------------------------------------------------------
        # 2. Resolve Storage Profile & Contexts (Section 5)
        # ---------------------------------------------------------------------
        storage_dict = request.storage_conditions.model_dump()
        constraints_dict = request.constraints.model_dump()

        # ---------------------------------------------------------------------
        # 3. Extract Packaging Requirements (Section 6)
        # ---------------------------------------------------------------------
        requirements = self.requirement_extractor.extract_requirements(
            commodity=commodity,
            storage=storage_dict,
            constraints=constraints_dict
        )

        # ---------------------------------------------------------------------
        # 4. Evaluate Scientific Rules & Screen Materials (Section 7 & 8)
        # ---------------------------------------------------------------------
        all_materials = get_verified_materials()
        detailed_screening = self.rule_filter_engine.screen_materials_detailed(
            commodity=commodity,
            materials=all_materials,
            storage=storage_dict,
            constraints=constraints_dict
        )

        eligible_materials = detailed_screening["eligible_materials"]
        rejected_materials = detailed_screening["rejected_materials"]
        evaluations = detailed_screening["evaluations"]

        # Build list of applied rule summaries for transparency
        applied_rules: List[RuleFilterResult] = []
        seen_rules = set()
        for ev in evaluations:
            for ch in ev.get("checks", []):
                r_name = ch.get("rule_name", "UnknownRule")
                if r_name not in seen_rules:
                    seen_rules.add(r_name)
                    applied_rules.append(RuleFilterResult(
                        rule_name=r_name,
                        passed=(ch.get("status") == "PASS"),
                        explanation=f"{ch.get('reason')} [{ch.get('source_id', 'SRC')}]"
                    ))

        # ---------------------------------------------------------------------
        # 5. Handle Case: Zero Materials Survived Hard Screening (Section 24)
        # ---------------------------------------------------------------------
        if len(eligible_materials) == 0:
            rejection_reasons = []
            for ev in evaluations:
                for fr in ev.get("failed_rules", []):
                    rejection_reasons.append({
                        "material_name": ev.get("material_name"),
                        "rule_name": fr.get("rule_name"),
                        "reason": fr.get("reason"),
                        "source_id": fr.get("source_id")
                    })

            summary_reasons = [
                f"{ev.get('material_name')}: {ev.get('failed_rules', [{}])[0].get('reason', 'Failed hard constraints')}"
                for ev in evaluations[:3] if ev.get("failed_rules")
            ]

            rejection_summary = {
                "evaluated_count": len(all_materials),
                "eligible_count": 0,
                "rejected_count": len(rejected_materials),
                "primary_rejection_reasons": summary_reasons,
                "all_rejection_details": rejection_reasons
            }

            return RecommendationResponse(
                request_id=request_id,
                timestamp=now,
                status="NO_ELIGIBLE_MATERIAL",
                rule_engine_status="COMPLETED",
                ml_status="INSUFFICIENT_VERIFIED_DATA",
                topsis_status="NOT_RUN",
                recommendation_status="NO_ELIGIBLE_MATERIAL",
                message=(
                    f"All {len(all_materials)} candidate packaging materials were eliminated by mandatory "
                    "safety or barrier constraints. Zero materials passed deterministic rule screening."
                ),
                recommended_material=None,
                primary_recommendation=None,
                alternative_materials=[],
                suggested_map=None,
                candidate_rankings=[],
                applied_rules=applied_rules,
                evidence_graph=[],
                explanation="No material passed all hard constraints: " + "; ".join(summary_reasons),
                dataset_version=self.DATASET_VERSION,
                rule_engine_version=RULE_ENGINE_VERSION,
                topsis_configuration_version=TOPSISDecisionEngine.CONFIG_VERSION,
                ml_model_version=None,
                rejection_summary=rejection_summary
            )

        # ---------------------------------------------------------------------
        # 6. TOPSIS Multi-Criteria Decision Making (MCDM) Ranking (Sections 9-15)
        # ---------------------------------------------------------------------
        mat_by_code: Dict[str, Dict[str, Any]] = {m["code"]: m for m in eligible_materials}
        candidate_ids = [m["code"] for m in eligible_materials]
        matrix_rows = []

        for m in eligible_materials:
            otr = float(m["otr_cc_m2_day_atm"])
            wvtr = float(m["wvtr_g_m2_day"])
            cost = float(m.get("cost_index_relative", 1.0))
            is_bio = m.get("is_biodegradable", False)
            co2_footprint = float(m.get("carbon_footprint_kg_co2_per_kg", 2.0))
            recyclability = int(m.get("recyclability_code", 7))

            # Criterion 1: Shelf Life / Barrier Efficacy (Benefit direction)
            # Logarithmic OTR transform: higher barrier = higher score
            shelf_life_score = round(10.0 / (1.0 + math.log10(1.0 + max(otr, 0.1))), 4)

            # Criterion 2: Overall Barrier Index (Benefit direction)
            barrier_score = round(
                (5.0 / (1.0 + math.log10(1.0 + max(otr, 0.1)))) + 
                (5.0 / (1.0 + math.log10(1.0 + max(wvtr, 0.1)))),
                4
            )

            # Criterion 3: Sustainability Score (Benefit direction)
            sustainability_score = 10.0 if is_bio else max(1.0, 9.0 - recyclability - (0.5 * co2_footprint))

            # Criterion 4: Cost Index (Cost direction - lower is preferred)
            cost_score = cost

            matrix_rows.append([shelf_life_score, barrier_score, sustainability_score, cost_score])

        decision_matrix = np.array(matrix_rows, dtype=float)
        weights = np.array([
            request.weights.shelf_life_weight,
            request.weights.barrier_performance_weight,
            request.weights.sustainability_weight,
            request.weights.cost_efficiency_weight
        ])
        benefit_mask = np.array([True, True, True, False])  # Cost is False (lower cost preferred)

        topsis_result = self.ranking_engine.rank_candidates_with_audit(
            decision_matrix=decision_matrix,
            weights=weights,
            benefit_criteria_mask=benefit_mask,
            candidate_ids=candidate_ids
        )
        topsis_ranks = topsis_result["rankings"]
        topsis_status_str = topsis_result.get("topsis_status", "COMPLETED")

        # ---------------------------------------------------------------------
        # 7. Format Candidate Rankings & Property Enrichment (Section 29)
        # ---------------------------------------------------------------------
        candidate_rankings: List[MaterialScoreResponse] = []
        for r in topsis_ranks:
            c_code = r["id"]
            c_mat = mat_by_code[c_code]
            c_idx = candidate_ids.index(c_code)
            candidate_rankings.append(MaterialScoreResponse(
                material_id=c_code,
                material_name=c_mat["name"],
                polymer_type=c_mat["polymer_type"],
                topsis_score=r["topsis_score"],
                rank=r["rank"],
                barrier_score=round(matrix_rows[c_idx][1], 2),
                sustainability_score=round(matrix_rows[c_idx][2], 2),
                cost_score=round(matrix_rows[c_idx][3], 2),
                otr_cc_m2_day_atm=float(c_mat["otr_cc_m2_day_atm"]),
                wvtr_g_m2_day=float(c_mat["wvtr_g_m2_day"]),
                thickness_micron=float(c_mat["thickness_micron"]),
                cost_index_relative=float(c_mat.get("cost_index_relative", 1.0)),
                is_biodegradable=bool(c_mat.get("is_biodegradable", False)),
                recyclability_code=int(c_mat.get("recyclability_code", 7))
            ))

        # ---------------------------------------------------------------------
        # 8. Primary Recommendation & Alternative Candidates (Sections 16 & 17)
        # ---------------------------------------------------------------------
        def build_material_response(mat_dict: Dict[str, Any]) -> PackagingMaterialResponse:
            m_id = uuid.uuid5(uuid.NAMESPACE_DNS, mat_dict["code"])
            return PackagingMaterialResponse(
                id=m_id,
                name=mat_dict["name"],
                code=mat_dict["code"],
                polymer_type=mat_dict["polymer_type"],
                description=mat_dict.get("description") or f"Candidate polymer film: {mat_dict['name']}",
                thickness_micron=mat_dict["thickness_micron"],
                otr_cc_m2_day_atm=mat_dict["otr_cc_m2_day_atm"],
                wvtr_g_m2_day=mat_dict["wvtr_g_m2_day"],
                tensile_strength_mpa=mat_dict.get("tensile_strength_mpa"),
                is_biodegradable=mat_dict["is_biodegradable"],
                biodegradation_standard=mat_dict.get("biodegradation_standard"),
                recyclability_code=mat_dict["recyclability_code"],
                cost_index_relative=mat_dict["cost_index_relative"],
                carbon_footprint_kg_co2_per_kg=mat_dict.get("carbon_footprint_kg_co2_per_kg"),
                food_contact_certified=mat_dict["food_contact_certified"],
                created_at=now,
                updated_at=now
            )

        top_code = topsis_ranks[0]["id"]
        primary_material = build_material_response(mat_by_code[top_code])

        # Alternatives: candidates ranked #2, #3, etc.
        alternatives: List[PackagingMaterialResponse] = [
            build_material_response(mat_by_code[r["id"]])
            for r in topsis_ranks[1:]
        ]

        # ---------------------------------------------------------------------
        # 9. Candidate MAP Formulation (Gorris & Peppelenbos 1992 / Sandhya 2010)
        # ---------------------------------------------------------------------
        suggested_map: Optional[MAPCompositionResponse] = None
        storage_temp = float(storage_dict.get("storage_temperature_c", 4.0))
        matched_map, map_status = self.map_selector.select_candidate_map(
            commodity_name=commodity["name"],
            category=commodity["category"],
            storage_temp_c=storage_temp
        )

        if matched_map:
            map_id = uuid.uuid5(uuid.NAMESPACE_DNS, matched_map["composition_name"])
            suggested_map = MAPCompositionResponse(
                id=map_id,
                composition_name=matched_map["composition_name"],
                description=matched_map.get("packaging_context"),
                oxygen_pct=matched_map["oxygen_pct"],
                carbon_dioxide_pct=matched_map["carbon_dioxide_pct"],
                nitrogen_pct=matched_map["nitrogen_pct"],
                target_application=matched_map["food_category"],
                created_at=now,
                updated_at=now
            )

        # ---------------------------------------------------------------------
        # 10. Generate Scientific Explanation & Evidence Graph (Sections 19 & 20)
        # ---------------------------------------------------------------------
        top_eval = next((ev for ev in evaluations if ev["material_code"] == top_code), {})
        explanation_obj = ExplanationGenerator.generate_candidate_explanation(top_eval)
        evidence_graph = ExplanationGenerator.build_evidence_graph(
            commodity=commodity,
            storage=storage_dict,
            requirements=requirements,
            eval_result=top_eval
        )

        explanation_text = (
            f"PRIMARY RECOMMENDATION: '{primary_material.name}' (Rank #1, TOPSIS closeness C*={topsis_ranks[0]['topsis_score']:.3f}). "
            f"Top-ranked option for the supplied requirements and configured criteria. "
            f"{explanation_obj['summary']} "
            f"Evaluated across {len(applied_rules)} deterministic scientific rules. "
            f"ASTM Standards: OTR tested under ASTM D3985 (23°C, 0% RH); WVTR tested under ASTM F1249 (37.8°C, 90% RH). "
            f"Food contact certified under FDA 21 CFR / FSSAI standards. "
            f"Machine Learning status: INSUFFICIENT_VERIFIED_DATA (ML models disarmed until verified multi-temperature degradation curves are ingested; recommendation derived deterministically via M2 Rules and TOPSIS MCDM)."
        )

        # ---------------------------------------------------------------------
        # 11. Audit Metadata (Section 31)
        # ---------------------------------------------------------------------
        audit_metadata = {
            "mcdm_engine": "TOPSIS",
            "commodity_name": commodity["name"],
            "storage_conditions": storage_dict,
            "weights_applied": {
                "shelf_life_weight": request.weights.shelf_life_weight,
                "barrier_performance_weight": request.weights.barrier_performance_weight,
                "sustainability_weight": request.weights.sustainability_weight,
                "cost_efficiency_weight": request.weights.cost_efficiency_weight
            },
            "criteria_configuration": [
                {
                    "criterion_id": c.criterion_id,
                    "name": c.name,
                    "unit": c.unit,
                    "direction": c.direction,
                    "source_basis": c.source_basis
                }
                for c in TOPSISDecisionEngine.get_default_criteria()
            ],
            "topsis_audit": topsis_result.get("audit", {}),
            "materials_evaluated_count": len(all_materials),
            "materials_eligible_count": len(eligible_materials),
            "materials_rejected_count": len(rejected_materials)
        }

        return RecommendationResponse(
            request_id=request_id,
            timestamp=now,
            status="COMPLETED",
            rule_engine_status="COMPLETED",
            ml_status="INSUFFICIENT_VERIFIED_DATA",
            topsis_status=topsis_status_str,
            recommendation_status="AVAILABLE_WITHOUT_ML",
            message=(
                f"Milestone M2/M4 Recommendation Intelligence completed: {len(eligible_materials)} of "
                f"{len(all_materials)} materials eligible after deterministic rule screening. "
                f"Ranked via TOPSIS MCDM. ML model status: INSUFFICIENT_VERIFIED_DATA."
            ),
            recommended_material=primary_material,
            primary_recommendation=primary_material,
            alternative_materials=alternatives,
            suggested_map=suggested_map,
            candidate_rankings=candidate_rankings,
            applied_rules=applied_rules,
            evidence_graph=evidence_graph,
            explanation=explanation_text,
            dataset_version=self.DATASET_VERSION,
            rule_engine_version=RULE_ENGINE_VERSION,
            topsis_configuration_version=TOPSISDecisionEngine.CONFIG_VERSION,
            ml_model_version=None,
            audit_metadata=audit_metadata
        )
