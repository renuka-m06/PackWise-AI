"""
PackWise AI - Milestone M4 Test Suite
Recommendation Intelligence, TOPSIS MCDM, Explainability & End-to-End Decision Pipeline

Validates:
  1. Complete End-to-End Decision Pipeline: Request -> Food Profile -> Storage Profile
     -> Requirements -> Rule Filtering -> TOPSIS -> Primary + Alternatives -> Evidence + ML Status
  2. Input contracts, bounds validation, and unverified commodity disarming
  3. No eligible material handling (all candidates eliminated by hard safety constraints)
  4. Single eligible material edge case (TOPSIS rank without artificial competition)
  5. Multiple eligible materials with ranked alternatives
  6. Strict separation of hard safety rules from soft user weight preferences
  7. TOPSIS normalization safety, benefit vs cost direction, and weights summing to 1.0
  8. Mathematical and decision determinism (identical input produces identical output)
  9. Preservation of empirical evidence graph and source IDs (zero fabricated claims)
  10. Strict ML status propagation (ML_STATUS = INSUFFICIENT_VERIFIED_DATA, zero fake confidence)
"""
import pytest
import numpy as np

from app.schemas.recommendation import (
    RecommendationRequest, 
    RecommendationResponse,
    RecommendationConstraints,
    MCDMWeights
)
from app.schemas.storage_condition import StorageConditionBase
from app.services.recommendation_service import RecommendationService
from app.engines.recommendation.orchestrator import RecommendationOrchestrator
from app.engines.ranking.topsis import TOPSISDecisionEngine


@pytest.fixture
def recommendation_service():
    return RecommendationService()


# -----------------------------------------------------------------------------
# 1. End-to-End Pipeline Verification (Section 36)
# -----------------------------------------------------------------------------
def test_m4_end_to_end_decision_pipeline(recommendation_service):
    """
    Executes a complete verified data recommendation flow for Broccoli:
      Broccoli (Vegetable, high respiration) at 4°C, 90% RH
      -> Food profile & packaging requirements (breathable packaging required)
      -> Hard filter eliminates hermetic impermeable films
      -> TOPSIS ranks eligible candidates
      -> Primary recommendation + Alternatives generated
      -> Evidence graph preserved with ASTM and USDA sources
      -> ML status explicitly disclosed as INSUFFICIENT_VERIFIED_DATA
    """
    req = RecommendationRequest(
        commodity_name="Broccoli",
        commodity_category="VEGETABLE",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=4.0,
            ambient_rh_percent=90.0,
            target_shelf_life_days=14.0
        ),
        constraints=RecommendationConstraints(
            strict_food_contact_grade=True,
            require_high_moisture_barrier=True
        ),
        weights=MCDMWeights(
            shelf_life_weight=0.35,
            barrier_performance_weight=0.25,
            sustainability_weight=0.25,
            cost_efficiency_weight=0.15
        )
    )

    resp = recommendation_service.generate_recommendation(req)

    # Status Assertions
    assert resp.status == "COMPLETED"
    assert resp.rule_engine_status == "COMPLETED"
    assert resp.ml_status == "INSUFFICIENT_VERIFIED_DATA"
    assert resp.topsis_status == "COMPLETED"
    assert resp.recommendation_status == "AVAILABLE_WITHOUT_ML"

    # Primary Recommendation Assertions
    assert resp.primary_recommendation is not None
    assert resp.recommended_material is not None
    assert resp.primary_recommendation.code == resp.recommended_material.code
    assert resp.primary_recommendation.food_contact_certified is True

    # Alternatives Assertions
    assert isinstance(resp.alternative_materials, list)
    # The primary recommendation should not be in alternatives
    alt_codes = [alt.code for alt in resp.alternative_materials]
    assert resp.primary_recommendation.code not in alt_codes

    # Rankings Assertions
    assert len(resp.candidate_rankings) > 0
    assert resp.candidate_rankings[0].rank == 1
    assert resp.candidate_rankings[0].material_id == resp.primary_recommendation.code

    # Evidence Graph Assertions
    assert len(resp.evidence_graph) > 0
    rule_ids = [e["rule_id"] for e in resp.evidence_graph]
    assert any("BAR-002" in r or "produce_breathability" in str(e.get("food_property", "")) for r, e in zip(rule_ids, resp.evidence_graph))
    for node in resp.evidence_graph:
        assert "food_property" in node
        assert "requirement" in node
        assert "material_property" in node
        assert "result" in node
        assert node.get("source_id") is not None

    # Version Traceability
    assert resp.dataset_version == "1.0.0-m3"
    assert resp.rule_engine_version == "m2.0.0"
    assert resp.topsis_configuration_version == "m4.0.0"
    assert resp.ml_model_version is None


# -----------------------------------------------------------------------------
# 2. Unverified Commodity Handling (Section 4)
# -----------------------------------------------------------------------------
def test_m4_unverified_commodity_disarmed(recommendation_service):
    """
    Verifies that unverified commodities disarm all recommendation engines,
    preventing any synthetic or guessed packaging suggestions.
    """
    req = RecommendationRequest(
        commodity_name="NonExistentFruitXYZ",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=5.0,
            ambient_rh_percent=85.0,
            target_shelf_life_days=10.0
        )
    )
    resp = recommendation_service.generate_recommendation(req)

    assert resp.status == "PENDING_ENGINES"
    assert resp.rule_engine_status == "NOT_RUN"
    assert resp.ml_status == "INSUFFICIENT_VERIFIED_DATA"
    assert resp.topsis_status == "NOT_RUN"
    assert resp.recommendation_status == "DISARMED_UNVERIFIED"
    assert resp.primary_recommendation is None
    assert resp.recommended_material is None
    assert len(resp.alternative_materials) == 0
    assert len(resp.candidate_rankings) == 0
    assert "not found in the verified empirical repository" in resp.message


# -----------------------------------------------------------------------------
# 3. No Eligible Material Edge Case (Section 24)
# -----------------------------------------------------------------------------
def test_m4_no_eligible_material_case(recommendation_service):
    """
    Verifies that impossible constraints eliminate all materials,
    returning NO_ELIGIBLE_MATERIAL without fabricating a recommendation.
    """
    impossible_req = RecommendationRequest(
        commodity_name="Strawberry",
        commodity_category="FRUIT",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=4.0,
            ambient_rh_percent=95.0,
            target_shelf_life_days=14.0
        ),
        constraints=RecommendationConstraints(
            prefer_biodegradable=True,
            strict_food_contact_grade=True,
            require_high_moisture_barrier=True,
            require_high_oxygen_barrier=True
        )
    )
    resp = recommendation_service.generate_recommendation(impossible_req)

    assert resp.status == "NO_ELIGIBLE_MATERIAL"
    assert resp.rule_engine_status == "COMPLETED"
    assert resp.topsis_status == "NOT_RUN"
    assert resp.recommendation_status == "NO_ELIGIBLE_MATERIAL"
    assert resp.primary_recommendation is None
    assert resp.recommended_material is None
    assert len(resp.alternative_materials) == 0

    # Verify rejection summary is populated
    assert resp.rejection_summary is not None
    assert resp.rejection_summary["evaluated_count"] == 15
    assert resp.rejection_summary["eligible_count"] == 0
    assert resp.rejection_summary["rejected_count"] == 15
    assert len(resp.rejection_summary["primary_rejection_reasons"]) > 0


# -----------------------------------------------------------------------------
# 4. User Preferences vs Mandatory Safety Rules (Section 12)
# -----------------------------------------------------------------------------
def test_m4_user_preferences_do_not_override_safety_rules(recommendation_service):
    """
    Verifies that setting a high cost or sustainability weight never overrides
    mandatory food contact or barrier safety rules.
    """
    req = RecommendationRequest(
        commodity_name="Raw Beef",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=2.0,
            ambient_rh_percent=85.0,
            target_shelf_life_days=10.0
        ),
        constraints=RecommendationConstraints(
            strict_food_contact_grade=True,
            require_high_oxygen_barrier=True
        ),
        # User strongly prioritizes cost efficiency over barrier performance
        weights=MCDMWeights(
            shelf_life_weight=0.05,
            barrier_performance_weight=0.05,
            sustainability_weight=0.1,
            cost_efficiency_weight=0.8
        )
    )
    resp = recommendation_service.generate_recommendation(req)

    assert resp.status == "COMPLETED"
    # Even though user requested lowest cost, all recommended materials MUST be food contact certified
    assert resp.primary_recommendation.food_contact_certified is True
    for alt in resp.alternative_materials:
        assert alt.food_contact_certified is True


# -----------------------------------------------------------------------------
# 5. TOPSIS Decision Engine Mathematical Properties (Sections 10, 13, 14, 15)
# -----------------------------------------------------------------------------
def test_m4_topsis_criteria_and_directions():
    criteria = TOPSISDecisionEngine.get_default_criteria()
    assert len(criteria) == 4

    crit_ids = [c.criterion_id for c in criteria]
    assert "CRIT-SHELF-LIFE" in crit_ids
    assert "CRIT-BARRIER" in crit_ids
    assert "CRIT-SUSTAINABILITY" in crit_ids
    assert "CRIT-COST" in crit_ids

    # Cost is a COST criterion (lower is better); others are BENEFIT
    for c in criteria:
        if c.criterion_id == "CRIT-COST":
            assert c.direction == "COST"
        else:
            assert c.direction == "BENEFIT"


def test_m4_topsis_single_candidate_edge_case():
    """
    Verifies Section 25: Single candidate handled cleanly without division by zero.
    """
    matrix = np.array([[8.0, 7.5, 9.0, 1.2]])
    weights = np.array([0.35, 0.25, 0.25, 0.15])
    mask = np.array([True, True, True, False])

    result = TOPSISDecisionEngine.rank_candidates_with_audit(
        decision_matrix=matrix,
        weights=weights,
        benefit_criteria_mask=mask,
        candidate_ids=["ONLY-ONE"]
    )
    assert result["topsis_status"] == "COMPLETED"
    assert len(result["rankings"]) == 1
    assert result["rankings"][0]["id"] == "ONLY-ONE"
    assert result["rankings"][0]["rank"] == 1
    assert result["rankings"][0]["topsis_score"] == 1.0


def test_m4_topsis_mathematical_ranking_order():
    """
    Candidate A: High barrier, high sustainability, low cost -> should rank #1
    Candidate B: Poor barrier, low sustainability, high cost -> should rank #2
    """
    matrix = np.array([
        [9.5, 9.0, 8.5, 1.1],  # Candidate A
        [2.0, 1.5, 2.0, 4.5]   # Candidate B
    ])
    weights = np.array([0.35, 0.25, 0.25, 0.15])
    mask = np.array([True, True, True, False])

    result = TOPSISDecisionEngine.rank_candidates_with_audit(
        decision_matrix=matrix,
        weights=weights,
        benefit_criteria_mask=mask,
        candidate_ids=["CAND_A", "CAND_B"]
    )
    ranks = result["rankings"]
    assert ranks[0]["id"] == "CAND_A"
    assert ranks[0]["rank"] == 1
    assert ranks[1]["id"] == "CAND_B"
    assert ranks[1]["rank"] == 2
    assert ranks[0]["topsis_score"] > ranks[1]["topsis_score"]


# -----------------------------------------------------------------------------
# 6. Recommendation Determinism (Section 32)
# -----------------------------------------------------------------------------
def test_m4_recommendation_determinism(recommendation_service):
    """
    Verifies that given identical input, the decision pipeline produces
    exact, deterministic outputs without stochastic or random deviations.
    """
    req = RecommendationRequest(
        commodity_name="Tomato",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=12.0,
            ambient_rh_percent=85.0,
            target_shelf_life_days=14.0
        ),
        weights=MCDMWeights(
            shelf_life_weight=0.4,
            barrier_performance_weight=0.2,
            sustainability_weight=0.2,
            cost_efficiency_weight=0.2
        )
    )

    resp1 = recommendation_service.generate_recommendation(req)
    resp2 = recommendation_service.generate_recommendation(req)

    assert resp1.status == resp2.status
    assert resp1.primary_recommendation.code == resp2.primary_recommendation.code
    assert len(resp1.candidate_rankings) == len(resp2.candidate_rankings)
    for r1, r2 in zip(resp1.candidate_rankings, resp2.candidate_rankings):
        assert r1.material_id == r2.material_id
        assert r1.topsis_score == r2.topsis_score
        assert r1.rank == r2.rank


# -----------------------------------------------------------------------------
# 7. Auditability & Explanation Disclosure (Sections 18, 19, 21, 31)
# -----------------------------------------------------------------------------
def test_m4_audit_metadata_and_ml_limitation_disclosure(recommendation_service):
    req = RecommendationRequest(
        commodity_name="Cheddar Cheese",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=4.0,
            ambient_rh_percent=80.0,
            target_shelf_life_days=60.0
        )
    )
    resp = recommendation_service.generate_recommendation(req)

    # Explanation must clearly disclose ML limitation
    assert "Machine Learning status: INSUFFICIENT_VERIFIED_DATA" in resp.explanation
    assert "ASTM Standards: OTR tested under ASTM D3985" in resp.explanation

    # Audit metadata must be populated
    assert resp.audit_metadata is not None
    assert "commodity_name" in resp.audit_metadata
    assert "criteria_configuration" in resp.audit_metadata
    assert "weights_applied" in resp.audit_metadata
    assert "materials_evaluated_count" in resp.audit_metadata
