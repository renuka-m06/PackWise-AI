import pytest
from app.core.data_validation import DataQualityValidator


def test_food_validation_ph_and_water_activity():
    validator = DataQualityValidator()

    # Valid food record
    valid = {
        "commodity_name": "Strawberry",
        "source_id": "SRC-FOOD-001",
        "pH_raw": "3.5",
        "water_activity_raw": "0.985",
        "moisture_content_raw": "91.0",
        "respiration_rate_raw": "22.0"
    }
    issues = validator.validate_food_record(valid, 0)
    assert len([i for i in issues if i.severity == "ERROR"]) == 0

    # Physically impossible pH (< 0 or > 14)
    invalid_ph = {**valid, "pH_raw": "16.5"}
    issues_ph = validator.validate_food_record(invalid_ph, 1)
    assert any(i.field_name == "pH" and i.issue_type == "INVALID_VALUE" for i in issues_ph)

    # Impossible water activity (aw > 1.0 or aw <= 0.0)
    invalid_aw = {**valid, "water_activity_raw": "1.25"}
    issues_aw = validator.validate_food_record(invalid_aw, 2)
    assert any(i.field_name == "water_activity" and i.issue_type == "INVALID_VALUE" for i in issues_aw)

    # Negative respiration rate
    invalid_resp = {**valid, "respiration_rate_raw": "-15.0"}
    issues_resp = validator.validate_food_record(invalid_resp, 3)
    assert any(i.field_name == "respiration_rate" and i.issue_type == "INVALID_VALUE" for i in issues_resp)


def test_packaging_validation_thickness_and_barriers():
    validator = DataQualityValidator()

    valid_pkg = {
        "material_name": "Standard LDPE",
        "source_id": "SRC-PKG-001",
        "thickness_raw": "25.0",
        "otr_raw": "7800.0",
        "wvtr_raw": "18.0",
        "recyclability_code": "4"
    }
    issues = validator.validate_material_record(valid_pkg, 0)
    assert len([i for i in issues if i.severity == "ERROR"]) == 0

    # Non-positive thickness
    invalid_thick = {**valid_pkg, "thickness_raw": "0.0"}
    issues_thick = validator.validate_material_record(invalid_thick, 1)
    assert any(i.field_name == "thickness" and i.issue_type == "INVALID_VALUE" for i in issues_thick)

    # Negative OTR
    invalid_otr = {**valid_pkg, "otr_raw": "-50.0"}
    issues_otr = validator.validate_material_record(invalid_otr, 2)
    assert any(i.field_name == "OTR" and i.issue_type == "INVALID_VALUE" for i in issues_otr)

    # Negative WVTR
    invalid_wvtr = {**valid_pkg, "wvtr_raw": "-5.0"}
    issues_wvtr = validator.validate_material_record(invalid_wvtr, 3)
    assert any(i.field_name == "WVTR" and i.issue_type == "INVALID_VALUE" for i in issues_wvtr)

    # Invalid recyclability code (must be 1-7)
    invalid_code = {**valid_pkg, "recyclability_code": "9"}
    issues_code = validator.validate_material_record(invalid_code, 4)
    assert any(i.field_name == "recyclability_code" and i.issue_type == "INVALID_VALUE" for i in issues_code)


def test_map_validation_gas_sum_and_tolerances():
    validator = DataQualityValidator()

    # Valid: 4% O2 + 12% CO2 + 84% N2 = 100%
    valid_map = {
        "composition_name": "Berry Mix",
        "source_id": "SRC-MAP-001",
        "o2_pct_raw": "4.0",
        "co2_pct_raw": "12.0",
        "n2_pct_raw": "84.0"
    }
    issues = validator.validate_map_record(valid_map, 0)
    assert len([i for i in issues if i.severity == "ERROR"]) == 0

    # Valid with slight rounding (e.g. 99.5% within 1.5% tolerance)
    valid_tolerance = {
        "composition_name": "Grain Flush",
        "source_id": "SRC-MAP-004",
        "o2_pct_raw": "0.5",
        "co2_pct_raw": "0.0",
        "n2_pct_raw": "99.0"
    }
    issues_tol = validator.validate_map_record(valid_tolerance, 1)
    assert len([i for i in issues_tol if i.severity == "ERROR"]) == 0

    # Invalid: sums to 80% (exceeds 1.5% tolerance)
    invalid_sum = {
        "composition_name": "Unbalanced Mix",
        "source_id": "SRC-MAP-001",
        "o2_pct_raw": "5.0",
        "co2_pct_raw": "10.0",
        "n2_pct_raw": "65.0"
    }
    issues_sum = validator.validate_map_record(invalid_sum, 2)
    assert any(i.field_name == "gas_sum" and i.issue_type == "INVALID_VALUE" for i in issues_sum)


def test_duplicate_detection():
    records = [
        {"code": "LDPE-25", "name": "Film A"},
        {"code": "HDPE-25", "name": "Film B"},
        {"code": "LDPE-25", "name": "Film A Duplicate"},  # Duplicate code
    ]

    deduped, issues = DataQualityValidator.detect_duplicates(records, unique_key_fields=["code"])
    assert len(deduped) == 2
    assert len(issues) == 1
    assert issues[0].issue_type == "DUPLICATE_RECORD"
