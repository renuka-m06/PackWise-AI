from app.engines.rules.barrier_rules import MoistureSensitivityRule, OxygenSensitivityRule
from app.engines.rules.safety_rules import FoodContactCertificationRule, BiodegradabilityConstraintRule
from app.engines.rules.filter_engine import RuleFilterEngine


def test_moisture_barrier_rule():
    rule = MoistureSensitivityRule()
    
    # Passing candidate: low WVTR
    result_pass = rule.evaluate(
        commodity={"moisture_sensitive": True},
        material={"wvtr_g_m2_day": 10.0},
        storage={"ambient_rh_percent": 85.0}
    )
    assert result_pass.passed is True

    # Failing candidate: excessive WVTR in high humidity
    result_fail = rule.evaluate(
        commodity={"moisture_sensitive": True},
        material={"wvtr_g_m2_day": 80.0},
        storage={"ambient_rh_percent": 90.0}
    )
    assert result_fail.passed is False
    assert "exceeds threshold" in result_fail.explanation


def test_oxygen_barrier_rule():
    rule = OxygenSensitivityRule()

    # Passing candidate: low OTR
    result_pass = rule.evaluate(
        commodity={"oxygen_sensitive": True},
        material={"otr_cc_m2_day_atm": 20.0},
        storage={}
    )
    assert result_pass.passed is True

    # Failing candidate: high OTR for oxygen sensitive item
    result_fail = rule.evaluate(
        commodity={"oxygen_sensitive": True},
        material={"otr_cc_m2_day_atm": 250.0},
        storage={}
    )
    assert result_fail.passed is False


def test_food_contact_rule():
    rule = FoodContactCertificationRule()

    result_certified = rule.evaluate({}, {"food_contact_certified": True}, {})
    assert result_certified.passed is True

    result_uncertified = rule.evaluate({}, {"food_contact_certified": False, "name": "Industrial Scrap"}, {})
    assert result_uncertified.passed is False


def test_rule_filter_engine_screening():
    engine = RuleFilterEngine()

    commodity = {"moisture_sensitive": True, "oxygen_sensitive": False}
    storage = {"ambient_rh_percent": 85.0}

    candidates = [
        {"name": "Valid Film", "wvtr_g_m2_day": 5.0, "otr_cc_m2_day_atm": 100.0, "food_contact_certified": True},
        {"name": "Leaky Moisture Film", "wvtr_g_m2_day": 95.0, "otr_cc_m2_day_atm": 100.0, "food_contact_certified": True},
        {"name": "Uncertified Film", "wvtr_g_m2_day": 5.0, "otr_cc_m2_day_atm": 100.0, "food_contact_certified": False},
    ]

    passed, rejected, audit_log = engine.screen_materials(commodity, candidates, storage)
    assert len(passed) == 1
    assert passed[0]["name"] == "Valid Film"
    assert len(rejected) == 2
    assert len(audit_log) > 0
