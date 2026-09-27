"""
PackWise AI - Milestone M2 Comprehensive Test Suite
Validates scientific deterministic rule engine, food requirement derivation,
barrier and safety constraints, MAP equilibrium, hard/soft separation,
explainability, determinism, and negative invariants.
"""
import pytest
from app.engines.rules.base import RuleStatus, RuleSeverity
from app.engines.rules.food_rules import FoodRequirementExtractor, PackagingRequirements
from app.engines.rules.safety_rules import (
    DataIntegrityRule,
    FoodContactCertificationRule,
    MAPPathogenSafetyRule,
    ChillingInjuryRule,
    BiodegradabilityConstraintRule
)
from app.engines.rules.storage_rules import StorageTemperatureCompatibilityRule
from app.engines.rules.barrier_rules import (
    OxygenBarrierRule,
    ProduceBreathabilityRule,
    MoistureBarrierRule
)
from app.engines.rules.map_rules import MAPCompatibilityRule, EmpiricalMAPSelector
from app.engines.rules.compatibility import MaterialCompatibilityEvaluator
from app.engines.rules.filter_engine import RuleFilterEngine, RULE_ENGINE_VERSION
from app.engines.rules.explanations import ExplanationGenerator
from app.engines.rules.config import get_rule_config
from app.engines.ranking.topsis import TOPSISDecisionEngine


# =============================================================================
# 1. FOOD REQUIREMENT & RESPIRATION RULES
# =============================================================================

def test_high_respiration_produce_requires_breathability():
    """High respiring produce (Broccoli at 10°C) must require breathable packaging (OTR >= 200)."""
    extractor = FoodRequirementExtractor()
    commodity = {
        "name": "Broccoli",
        "category": "VEGETABLE",
        "respiration_rate_mg_co2_kg_hr": 48.0,
        "optimal_temperature_min_c": 0.0,
        "optimal_temperature_max_c": 1.0,
        "moisture_sensitive": True,
        "oxygen_sensitive": True
    }
    storage = {"storage_temperature_c": 10.0, "ambient_rh_percent": 90.0}
    req = extractor.extract_requirements(commodity, storage)

    assert req.respiration_status == "RESPIRING"
    assert req.respiration_rate_at_storage_temp == 81.0
    assert req.breathable_packaging_required is True
    assert req.min_acceptable_otr == 200.0


def test_low_respiration_produce():
    """Low respiring produce (Apple at 0°C, rate = 3.0) does not trigger high breathability requirement."""
    extractor = FoodRequirementExtractor()
    commodity = {
        "name": "Apple",
        "category": "FRUIT",
        "optimal_temperature_min_c": -1.0,
        "optimal_temperature_max_c": 4.0,
        "moisture_sensitive": False,
        "oxygen_sensitive": True
    }
    storage = {"storage_temperature_c": 0.0, "ambient_rh_percent": 90.0}
    req = extractor.extract_requirements(commodity, storage)

    assert req.respiration_status == "RESPIRING"
    assert req.respiration_rate_at_storage_temp == 3.0
    assert req.breathable_packaging_required is False


def test_respiration_temperature_mismatch_never_extrapolates():
    """
    CRITICAL ANTI-FABRICATION RULE:
    When storage temperature (e.g. 15.0°C) lacks an empirical observation,
    the system MUST mark UNKNOWN_TEMPERATURE and NEVER fabricate or interpolate a rate.
    """
    extractor = FoodRequirementExtractor()
    commodity = {
        "name": "Strawberry",
        "category": "FRUIT",
        "optimal_temperature_min_c": 0.0,
        "optimal_temperature_max_c": 1.0
    }
    # Observations exist at 0°C, 5°C, 10°C, 20°C. 15.0°C has no empirical data.
    storage = {"storage_temperature_c": 15.0, "ambient_rh_percent": 85.0}
    req = extractor.extract_requirements(commodity, storage)

    assert req.respiration_status == "UNKNOWN_TEMPERATURE"
    assert req.respiration_rate_at_storage_temp is None
    # Verify zero extrapolation evidence was added
    evidence_text = str(req.evidence)
    assert "Zero extrapolation policy enforced" in evidence_text


def test_non_respiring_commodity():
    """Non-respiring food (Raw Beef, Cheese) must be flagged NON_RESPIRING with no breathability requirement."""
    extractor = FoodRequirementExtractor()
    commodity = {
        "name": "Raw Beef",
        "category": "MEAT",
        "water_activity_aw": 0.99,
        "oxygen_sensitive": True,
        "moisture_sensitive": True
    }
    storage = {"storage_temperature_c": 2.0, "ambient_rh_percent": 85.0}
    req = extractor.extract_requirements(commodity, storage)

    assert req.respiration_status == "NON_RESPIRING"
    assert req.breathable_packaging_required is False
    assert req.oxygen_barrier_required is True


# =============================================================================
# 2. BARRIER RULES (OTR & WVTR)
# =============================================================================

def test_oxygen_barrier_valid_material():
    """Material with OTR <= limit satisfies oxygen barrier rule under ASTM D3985."""
    rule = OxygenBarrierRule()
    commodity = {"oxygen_sensitive": True}
    material = {"name": "EVOH Film", "otr_cc_m2_day_atm": 0.5}
    storage = {}

    res = rule.evaluate(commodity, material, storage)
    assert res.status == RuleStatus.PASS.value
    assert res.passed is True
    assert "ASTM D3985" in res.reason


def test_oxygen_barrier_invalid_material():
    """Material with OTR > limit fails oxygen barrier rule with exact comparison reason."""
    rule = OxygenBarrierRule()
    commodity = {"oxygen_sensitive": True}
    material = {"name": "Porous LDPE", "otr_cc_m2_day_atm": 2500.0}
    storage = {}

    res = rule.evaluate(commodity, material, storage)
    assert res.status == RuleStatus.FAIL.value
    assert res.passed is False
    assert res.severity == RuleSeverity.HARD.value
    assert "exceeds maximum permitted limit" in res.reason


def test_oxygen_barrier_missing_otr_yields_insufficient_data():
    """When material OTR is missing, rule returns INSUFFICIENT_DATA and NEVER converts to PASS."""
    rule = OxygenBarrierRule()
    commodity = {"oxygen_sensitive": True}
    material = {"name": "Uncharacterized Film", "otr_cc_m2_day_atm": None}
    storage = {}

    res = rule.evaluate(commodity, material, storage)
    assert res.status == RuleStatus.INSUFFICIENT_DATA.value
    assert res.passed is False
    assert "lacks verified OTR" in res.reason


def test_produce_breathability_rejects_impermeable_film():
    """Highly respiring produce placed in impermeable barrier film (< 50 OTR) must fail to prevent suffocation."""
    rule = ProduceBreathabilityRule()
    commodity = {"name": "Broccoli", "respiration_rate_mg_co2_kg_hr": 48.0}
    material = {"name": "Impermeable EVOH Foil", "otr_cc_m2_day_atm": 1.0}
    storage = {}

    res = rule.evaluate(commodity, material, storage)
    assert res.status == RuleStatus.FAIL.value
    assert res.passed is False
    assert "anaerobic fermentation" in res.reason


def test_wvtr_valid_and_invalid():
    """Evaluates valid vs leaky WVTR under ASTM F1249 for moisture-sensitive commodity."""
    rule = MoistureBarrierRule()
    commodity = {"moisture_sensitive": True}

    good_film = {"name": "High Barrier BOPP", "wvtr_g_m2_day": 4.0}
    bad_film = {"name": "Leaky Cellophane", "wvtr_g_m2_day": 120.0}

    res_good = rule.evaluate(commodity, good_film, {})
    assert res_good.status == RuleStatus.PASS.value

    res_bad = rule.evaluate(commodity, bad_film, {})
    assert res_bad.status == RuleStatus.FAIL.value
    assert "ASTM F1249" in res_bad.reason


def test_wvtr_missing_yields_insufficient_data():
    """Missing WVTR must return INSUFFICIENT_DATA."""
    rule = MoistureBarrierRule()
    res = rule.evaluate({"moisture_sensitive": True}, {"name": "No WVTR", "wvtr_g_m2_day": None}, {})
    assert res.status == RuleStatus.INSUFFICIENT_DATA.value
    assert res.passed is False


# =============================================================================
# 3. SAFETY RULES
# =============================================================================

def test_food_contact_hard_elimination():
    """Material lacking statutory food-contact certification must fail HARD."""
    rule = FoodContactCertificationRule()
    res = rule.evaluate({}, {"name": "Recycled Trash Film", "food_contact_certified": False}, {})
    assert res.status == RuleStatus.FAIL.value
    assert res.severity == RuleSeverity.HARD.value
    assert res.passed is False
    assert "lacks food contact grade certification" in res.reason


def test_food_contact_missing_data_fails_safely():
    """Material with None food_contact_certified must return INSUFFICIENT_DATA with HARD severity."""
    rule = FoodContactCertificationRule()
    res = rule.evaluate({}, {"name": "Unknown Film", "food_contact_certified": None}, {})
    assert res.status == RuleStatus.INSUFFICIENT_DATA.value
    assert res.severity == RuleSeverity.HARD.value
    assert res.passed is False


def test_map_pathogen_safety_rule():
    """
    Non-acid produce (pH 6.5 > 4.6) stored at warm temperature (5°C) inside
    impermeable film (OTR = 10) must fail due to C. botulinum neurotoxin risk.
    """
    rule = MAPPathogenSafetyRule()
    commodity = {"name": "Cut Broccoli", "category": "VEGETABLE", "pH": 6.5}
    material = {"name": "Hermetic Barrier Film", "otr_cc_m2_day_atm": 10.0}
    storage = {"storage_temperature_c": 5.0}

    res = rule.evaluate(commodity, material, storage)
    assert res.status == RuleStatus.FAIL.value
    assert res.severity == RuleSeverity.HARD.value
    assert "botulism" in res.reason.lower()


def test_chilling_injury_rule():
    """Storage of Banana (chilling threshold 13°C) at 4°C must fail chilling injury rule."""
    rule = ChillingInjuryRule()
    commodity = {"name": "Banana"}
    storage = {"storage_temperature_c": 4.0}

    res = rule.evaluate(commodity, {}, storage)
    assert res.status == RuleStatus.FAIL.value
    assert res.severity == RuleSeverity.HARD.value
    assert "chilling injury threshold (13.0°C)" in res.reason


def test_frozen_storage_polymer_brittleness():
    """Deep freeze (-18°C) must eliminate brittle biopolymers (PLA, Cellophane)."""
    rule = StorageTemperatureCompatibilityRule()
    storage = {"storage_temperature_c": -18.0}
    pla_mat = {"name": "Ingeo PLA", "polymer_type": "PLA"}
    pe_mat = {"name": "LDPE Film", "polymer_type": "LDPE"}

    res_pla = rule.evaluate({}, pla_mat, storage)
    assert res_pla.status == RuleStatus.FAIL.value
    assert "brittle fracture" in res_pla.reason

    res_pe = rule.evaluate({}, pe_mat, storage)
    assert res_pe.status == RuleStatus.PASS.value


# =============================================================================
# 4. MAP RULES
# =============================================================================

def test_map_gas_sum_valid_and_invalid():
    """Valid MAP sums to 100% +- 1.5%; invalid gas sum must FAIL."""
    rule = MAPCompatibilityRule()

    valid_map = {"oxygen_pct": 4.0, "carbon_dioxide_pct": 12.0, "nitrogen_pct": 84.0}
    invalid_map = {"oxygen_pct": 20.0, "carbon_dioxide_pct": 30.0, "nitrogen_pct": 80.0}  # Sum = 130%

    res_valid = rule.evaluate({"map_composition": valid_map}, {"otr_cc_m2_day_atm": 50.0}, {})
    assert res_valid.status == RuleStatus.PASS.value

    res_invalid = rule.evaluate({"map_composition": invalid_map}, {"otr_cc_m2_day_atm": 50.0}, {})
    assert res_invalid.status == RuleStatus.FAIL.value
    assert "violate physical gas balance" in res_invalid.reason


def test_map_selector_insufficient_data_for_unverified_category():
    """EmpiricalMAPSelector must return INSUFFICIENT_DATA rather than guessing a formulation."""
    selector = EmpiricalMAPSelector()
    matched, status = selector.select_candidate_map(
        commodity_name="Exotic Seaweed",
        category="AQUATIC_WEED",
        storage_temp_c=4.0
    )
    assert matched is None
    assert status == "INSUFFICIENT_DATA"


# =============================================================================
# 5. HARD CONSTRAINTS VS SOFT CRITERIA
# =============================================================================

def test_hard_vs_soft_constraints_separation():
    """
    Verify that:
    - HARD failure -> material is REJECTED (is_eligible = False)
    - SOFT failure (e.g. non-biodegradable when preferred, or high cost) -> material remains ELIGIBLE (is_eligible = True)
    """
    evaluator = MaterialCompatibilityEvaluator()
    commodity = {"name": "Apple", "category": "FRUIT", "oxygen_sensitive": False}
    storage = {"storage_temperature_c": 4.0, "ambient_rh_percent": 80.0}

    # Material with hard failure (food contact false)
    hard_fail_mat = {
        "name": "Toxic Foil",
        "thickness_micron": 25.0,
        "food_contact_certified": False,
        "is_biodegradable": True
    }
    res_hard = evaluator.evaluate_material(commodity, storage, hard_fail_mat)
    assert res_hard["status"] == "REJECTED"
    assert res_hard["is_eligible"] is False
    assert len(res_hard["failed_rules"]) >= 1

    # Material with soft failure (cost exceeds preference, non-biodegradable when preferred)
    soft_fail_mat = {
        "name": "Expensive Clean LDPE",
        "code": "LDPE-CLEAN",
        "polymer_type": "LDPE",
        "thickness_micron": 50.0,
        "otr_cc_m2_day_atm": 3900.0,
        "wvtr_g_m2_day": 9.0,
        "food_contact_certified": True,
        "is_biodegradable": False,
        "cost_index_relative": 4.5
    }
    constraints = {"prefer_biodegradable": True, "max_acceptable_cost_index": 2.0}
    res_soft = evaluator.evaluate_material(commodity, storage, soft_fail_mat, constraints=constraints)
    assert res_soft["status"] == "ELIGIBLE"
    assert res_soft["is_eligible"] is True
    assert len(res_soft["warnings"]) >= 2
    assert len(res_soft["failed_rules"]) == 0


# =============================================================================
# 6. EXPLAINABILITY & EVIDENCE GRAPHS
# =============================================================================

def test_explainability_all_results_have_reasons():
    """Every rule evaluation MUST provide an explicit human-readable reason."""
    evaluator = MaterialCompatibilityEvaluator()
    commodity = {"name": "Strawberry", "category": "FRUIT", "oxygen_sensitive": True, "moisture_sensitive": True}
    storage = {"storage_temperature_c": 4.0, "ambient_rh_percent": 90.0}
    material = {
        "name": "PLA 25um",
        "code": "PLA-25",
        "polymer_type": "PLA",
        "thickness_micron": 25.0,
        "otr_cc_m2_day_atm": 550.0,
        "wvtr_g_m2_day": 175.0,
        "food_contact_certified": True,
        "is_biodegradable": True
    }

    eval_res = evaluator.evaluate_material(commodity, storage, material)
    explanation = ExplanationGenerator.generate_candidate_explanation(eval_res)

    assert "summary" in explanation
    assert len(explanation["why_passed"]) > 0 or len(explanation["why_failed"]) > 0
    for check in eval_res["checks"]:
        assert len(check["reason"]) > 5
        assert check["status"] in ["PASS", "FAIL", "INSUFFICIENT_DATA"]


def test_evidence_graph_structure():
    """Evidence graph must connect food property -> requirement -> rule -> material -> source."""
    evaluator = MaterialCompatibilityEvaluator()
    commodity = {"name": "Broccoli", "category": "VEGETABLE", "oxygen_sensitive": True}
    storage = {"storage_temperature_c": 1.0, "ambient_rh_percent": 95.0}
    material = {
        "name": "BOPP 20um",
        "code": "BOPP-20",
        "polymer_type": "PP",
        "thickness_micron": 20.0,
        "otr_cc_m2_day_atm": 1600.0,
        "wvtr_g_m2_day": 4.2,
        "food_contact_certified": True
    }

    eval_res = evaluator.evaluate_material(commodity, storage, material)
    graph = ExplanationGenerator.build_evidence_graph(commodity, storage, None, eval_res)

    assert len(graph) > 0
    node = graph[0]
    assert "food_property" in node
    assert "requirement" in node
    assert "rule_id" in node
    assert "material_property" in node
    assert "result" in node
    assert "source_id" in node


# =============================================================================
# 7. DETERMINISM
# =============================================================================

def test_rule_engine_determinism():
    """Executing the engine multiple times with identical inputs must produce bit-for-bit identical results."""
    engine = RuleFilterEngine()
    commodity = {"name": "Strawberry", "category": "FRUIT", "oxygen_sensitive": True, "moisture_sensitive": True}
    storage = {"storage_temperature_c": 4.0, "ambient_rh_percent": 90.0}
    candidates = [
        {"name": "LDPE-25", "thickness_micron": 25.0, "otr_cc_m2_day_atm": 7800.0, "wvtr_g_m2_day": 18.0, "food_contact_certified": True},
        {"name": "EVOH-15", "thickness_micron": 15.0, "otr_cc_m2_day_atm": 0.5, "wvtr_g_m2_day": 45.0, "food_contact_certified": True},
    ]

    res1 = engine.screen_materials_detailed(commodity, candidates, storage)
    res2 = engine.screen_materials_detailed(commodity, candidates, storage)

    assert res1["eligible_count"] == res2["eligible_count"]
    assert res1["rejected_count"] == res2["rejected_count"]
    assert [c["status"] for c in res1["evaluations"]] == [c["status"] for c in res2["evaluations"]]


# =============================================================================
# 8. NEGATIVE TESTS
# =============================================================================

def test_negative_never_recommend_failed_safety():
    """A material failing food contact certification must NEVER survive to eligible set."""
    engine = RuleFilterEngine()
    candidates = [
        {"name": "Industrial Recycled Scrap", "food_contact_certified": False, "otr_cc_m2_day_atm": 10.0, "wvtr_g_m2_day": 1.0}
    ]
    passed, rejected, _ = engine.screen_materials({}, candidates, {})
    assert len(passed) == 0
    assert len(rejected) == 1


def test_negative_never_treat_missing_data_as_pass():
    """Missing mandatory measurements (e.g. OTR for oxygen sensitive item) must NOT pass."""
    rule = OxygenBarrierRule()
    res = rule.evaluate({"oxygen_sensitive": True}, {"name": "No OTR", "otr_cc_m2_day_atm": None}, {})
    assert res.passed is False
    assert res.status == RuleStatus.INSUFFICIENT_DATA.value


def test_negative_topsis_never_ranks_rejected_material():
    """Materials eliminated by hard constraints must NEVER be passed to TOPSIS."""
    engine = RuleFilterEngine()
    candidates = [
        {"name": "Failed Safety", "code": "FS-1", "food_contact_certified": False, "otr_cc_m2_day_atm": 10.0, "wvtr_g_m2_day": 1.0},
        {"name": "Good Material", "code": "GM-1", "thickness_micron": 25.0, "food_contact_certified": True, "otr_cc_m2_day_atm": 100.0, "wvtr_g_m2_day": 5.0}
    ]
    passed, rejected, _ = engine.screen_materials({"moisture_sensitive": True}, candidates, {})

    assert len(passed) == 1
    assert passed[0]["code"] == "GM-1"
    assert "FS-1" not in [m["code"] for m in passed]
