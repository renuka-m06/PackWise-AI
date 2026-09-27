"""
PackWise AI - Recommendation Pipeline Orchestrator (Milestone M2)
Executes the deterministic decision pipeline:
  REQUEST -> COMMODITY PROFILE -> STORAGE CONDITIONS -> REQUIREMENTS
  -> SCIENTIFIC RULE SCREENING -> ELIGIBLE MATERIALS -> TOPSIS MCDM RANKING
  -> PRIMARY RECOMMENDATION & EXPLANATION
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
from app.engines.rules.map_rules import EmpiricalMAPSelector
from app.engines.rules.explanations import ExplanationGenerator
from app.engines.ranking.topsis import TOPSISDecisionEngine
from app.db.empirical_data import (
    get_verified_commodity,
    get_verified_materials
)


class RecommendationOrchestrator:
    """
    Orchestrates the scientific recommendation pipeline:
      USER INPUT -> COMMODITY -> STORAGE -> REQUIREMENTS
      -> RULE-BASED FILTERING -> TOPSIS MCDM RANKING -> RECOMMENDATION & EXPLANATION
    """
    def __init__(self):
        self.rule_filter_engine = RuleFilterEngine()
        self.ranking_engine = TOPSISDecisionEngine()
        self.map_selector = EmpiricalMAPSelector()

    def process_recommendation_request(self, request: RecommendationRequest) -> RecommendationResponse:
        request_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # ---------------------------------------------------------------------
        # 1. Load Verified Commodity
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
                suggested_map=None,
                candidate_rankings=[],
                applied_rules=[
                    RuleFilterResult(
                        rule_name="M0ContractValidationRule",
                        passed=True,
                        explanation=f"Commodity '{request.commodity_name}' parameters validated against Pydantic schema."
                    )
                ],
                explanation="To execute M2 recommendations, choose a verified commodity from the catalog (e.g., Strawberry, Broccoli, Apple, Tomato, Raw Beef, Cheddar Cheese)."
            )

        # ---------------------------------------------------------------------
        # 2. Extract Storage and Constraints Contexts
        # ---------------------------------------------------------------------
        storage_dict = request.storage_conditions.model_dump()
        constraints_dict = request.constraints.model_dump()

        # ---------------------------------------------------------------------
        # 3. Load Verified Candidate Materials & Run Rule Screening
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
        # 4. Handle Case: Zero Materials Survived Hard Screening
        # ---------------------------------------------------------------------
        if len(eligible_materials) == 0:
            primary_rejection_reasons = [
                f"{ev.get('material_name')}: {ev.get('failed_rules', [{}])[0].get('reason', 'Failed hard constraints')}"
                for ev in evaluations[:3] if ev.get("failed_rules")
            ]
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
                suggested_map=None,
                candidate_rankings=[],
                applied_rules=applied_rules,
                explanation="No material passed all hard constraints: " + "; ".join(primary_rejection_reasons)
            )

        # ---------------------------------------------------------------------
        # 5. TOPSIS Multi-Criteria Decision Making (MCDM) Ranking
        # ---------------------------------------------------------------------
        # Build Decision Matrix: [Shelf Life Index, Barrier Score, Sustainability Score, Cost Index]
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

            # Criterion 1: Shelf Life / Barrier Efficacy (Benefit)
            # Higher barrier = longer shelf life, measured on logarithmic scale
            shelf_life_score = round(10.0 / (1.0 + math.log10(1.0 + max(otr, 0.1))), 4)

            # Criterion 2: Overall Barrier Index (Benefit)
            barrier_score = round(
                (5.0 / (1.0 + math.log10(1.0 + max(otr, 0.1)))) + 
                (5.0 / (1.0 + math.log10(1.0 + max(wvtr, 0.1)))),
                4
            )

            # Criterion 3: Sustainability Score (Benefit)
            # Compostable receives high base; polyolefins scored by recyclability
            sustainability_score = 10.0 if is_bio else max(1.0, 9.0 - recyclability - (0.5 * co2_footprint))

            # Criterion 4: Cost Index (Cost - lower is better)
            cost_score = cost

            matrix_rows.append([shelf_life_score, barrier_score, sustainability_score, cost_score])

        decision_matrix = np.array(matrix_rows, dtype=float)
        weights = np.array([
            request.weights.shelf_life_weight,
            request.weights.barrier_performance_weight,
            request.weights.sustainability_weight,
            request.weights.cost_efficiency_weight
        ])
        benefit_mask = np.array([True, True, True, False])  # Cost is False (lower preferred)

        topsis_ranks = self.ranking_engine.rank_candidates(
            decision_matrix=decision_matrix,
            weights=weights,
            benefit_criteria_mask=benefit_mask,
            candidate_ids=candidate_ids
        )

        # ---------------------------------------------------------------------
        # 6. Format Candidate Rankings & Primary Recommendation
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
                cost_score=round(matrix_rows[c_idx][3], 2)
            ))

        top_code = topsis_ranks[0]["id"]
        top_mat = mat_by_code[top_code]

        # Generate deterministic UUID from polymer code
        top_id = uuid.uuid5(uuid.NAMESPACE_DNS, top_mat["code"])
        recommended_material = PackagingMaterialResponse(
            id=top_id,
            name=top_mat["name"],
            code=top_mat["code"],
            polymer_type=top_mat["polymer_type"],
            description=top_mat.get("description") or f"Optimal candidate polymer: {top_mat['name']}",
            thickness_micron=top_mat["thickness_micron"],
            otr_cc_m2_day_atm=top_mat["otr_cc_m2_day_atm"],
            wvtr_g_m2_day=top_mat["wvtr_g_m2_day"],
            tensile_strength_mpa=top_mat.get("tensile_strength_mpa"),
            is_biodegradable=top_mat["is_biodegradable"],
            biodegradation_standard=top_mat.get("biodegradation_standard"),
            recyclability_code=top_mat["recyclability_code"],
            cost_index_relative=top_mat["cost_index_relative"],
            carbon_footprint_kg_co2_per_kg=top_mat.get("carbon_footprint_kg_co2_per_kg"),
            food_contact_certified=top_mat["food_contact_certified"],
            created_at=now,
            updated_at=now
        )

        # ---------------------------------------------------------------------
        # 7. Select Candidate MAP Formulation
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
        # 8. Generate Scientific Explanation
        # ---------------------------------------------------------------------
        top_eval = next((ev for ev in evaluations if ev["material_code"] == top_code), {})
        explanation_obj = ExplanationGenerator.generate_candidate_explanation(top_eval)

        explanation_text = (
            f"PRIMARY SELECTION: '{recommended_material.name}' (Rank #1, TOPSIS C*={topsis_ranks[0]['topsis_score']:.3f}). "
            f"{explanation_obj['summary']} "
            f"Evaluated across {len(applied_rules)} deterministic scientific rules. "
            f"ASTM Standards: OTR tested under ASTM D3985 (23°C, 0% RH); WVTR tested under ASTM F1249 (37.8°C, 90% RH). "
            f"Food contact verified under FDA 21 CFR / FSSAI standards. "
            f"Machine Learning model status: DEFERRED (insufficient kinetic time-series curves)."
        )

        return RecommendationResponse(
            request_id=request_id,
            timestamp=now,
            status="COMPLETED",
            rule_engine_status="COMPLETED",
            ml_status="INSUFFICIENT_VERIFIED_DATA",
            topsis_status="COMPLETED",
            recommendation_status="AVAILABLE_WITHOUT_ML",
            message=(
                f"Milestone M2/M3 Scientific Recommendation Engine completed: {len(eligible_materials)} of "
                f"{len(all_materials)} materials eligible after deterministic rule screening. "
                "Ranked via TOPSIS MCDM. ML model status: INSUFFICIENT_VERIFIED_DATA."
            ),
            recommended_material=recommended_material,
            suggested_map=suggested_map,
            candidate_rankings=candidate_rankings,
            applied_rules=applied_rules,
            explanation=explanation_text
        )
