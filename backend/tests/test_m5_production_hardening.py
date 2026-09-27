"""
PackWise AI - Production Hardening & Operational Resilience Test Suite (Milestone M5)
Verifies:
1. Health and subsystem readiness contracts (Health vs Readiness)
2. Request ID tracking & propagation (X-Request-ID)
3. Security headers (MIME-sniffing, clickjacking, XSS)
4. Structured error responses (404, 422, 400) without stack trace leakage
5. Request validation bounds (NaN, Infinity, empty names, negative weights)
6. Recommendation audit history persistence & retrieval
7. Catalog single-item lookups (materials & commodities)
8. Zero-fabrication and ML fallback disclosures
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Health vs Readiness Separation (Section 4)
# -----------------------------------------------------------------------------

def test_m5_health_liveness_contract():
    """Verifies that /health remains a lightweight liveness probe."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "foodpack-api"
    assert "timestamp" in data


def test_m5_readiness_subsystems_contract():
    """
    Verifies that /readiness inspects all core subsystems.
    Crucially: ML being DATA_GATED does not fail overall readiness.
    """
    resp = client.get("/api/v1/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("READY", "DEGRADED")
    components = data["components"]

    # API gateway must be ready
    assert components["api"]["status"] == "READY"

    # Empirical dataset must be ready with verified counts
    assert components["empirical_dataset"]["status"] == "READY"
    assert components["empirical_dataset"]["details"]["commodities_count"] >= 15
    assert components["empirical_dataset"]["details"]["materials_count"] >= 15
    assert components["empirical_dataset"]["details"]["zero_synthetic_data"] is True

    # Rule engine must be active
    assert components["rule_engine"]["status"] == "READY"
    assert components["rule_engine"]["details"]["version"] == "m2.0.0"

    # TOPSIS MCDM must be active
    assert components["topsis"]["status"] == "READY"
    assert components["topsis"]["details"]["version"] == "m4.0.0"

    # ML must be DATA_GATED without failing overall readiness
    assert components["ml"]["status"] == "DATA_GATED"
    assert components["ml"]["details"]["ml_status"] == "INSUFFICIENT_VERIFIED_DATA"


# -----------------------------------------------------------------------------
# 2. Request ID Tracking & Latency Telemetry (Section 10)
# -----------------------------------------------------------------------------

def test_m5_request_id_generated_when_absent():
    """Verifies server generates UUID4 when client omits X-Request-ID."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert "X-Process-Time-Ms" in resp.headers
    generated_id = resp.headers["X-Request-ID"]
    # Check it parses as valid UUID
    parsed = uuid.UUID(generated_id)
    assert str(parsed) == generated_id


def test_m5_request_id_preserved_when_supplied():
    """Verifies server preserves client's correlation trace ID."""
    custom_trace_id = "trace-test-audit-9999"
    resp = client.get("/api/v1/health", headers={"X-Request-ID": custom_trace_id})
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == custom_trace_id


# -----------------------------------------------------------------------------
# 3. Security Headers Enforcement (Section 7)
# -----------------------------------------------------------------------------

def test_m5_security_headers_present():
    """Verifies that mandatory HTTP security headers are set on all responses."""
    resp = client.get("/api/v1/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


# -----------------------------------------------------------------------------
# 4. Structured Error Responses (Section 5)
# -----------------------------------------------------------------------------

def test_m5_structured_error_on_not_found():
    """Verifies 404 returns structured JSON error without exposing server internals."""
    resp = client.get("/api/v1/recommendations/non-existent-uuid-12345")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "non-existent-uuid-12345" in data["error"]["message"]
    assert "request_id" in data


def test_m5_structured_error_on_validation_failure():
    """Verifies 422 returns structured JSON error detailing field validation issues."""
    resp = client.post("/api/v1/recommendations", json={
        "commodity_name": "",  # Empty name is invalid
        "storage_conditions": {
            "storage_temperature_c": 100.0,  # Impossible temperature > 50°C
            "ambient_rh_percent": -5.0,     # Negative RH is invalid
            "target_shelf_life_days": 0     # < 1 day is invalid
        }
    })
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "validation_errors" in data["error"]["details"]
    assert len(data["error"]["details"]["validation_errors"]) > 0


# -----------------------------------------------------------------------------
# 5. Input Bounds Hardening (Section 6)
# -----------------------------------------------------------------------------

def test_m5_rejects_nan_and_infinity_in_storage_conditions():
    """Verifies that NaN and Infinity are strictly rejected in numeric fields."""
    # Test NaN temperature
    resp = client.post("/api/v1/recommendations", json={
        "commodity_name": "Strawberry",
        "storage_conditions": {
            "storage_temperature_c": "nan",
            "ambient_rh_percent": 90.0,
            "target_shelf_life_days": 7.0
        }
    })
    assert resp.status_code == 422

    # Test Infinity RH
    resp_inf = client.post("/api/v1/recommendations", json={
        "commodity_name": "Strawberry",
        "storage_conditions": {
            "storage_temperature_c": 4.0,
            "ambient_rh_percent": "inf",
            "target_shelf_life_days": 7.0
        }
    })
    assert resp_inf.status_code == 422


def test_m5_rejects_nan_and_infinity_in_mcdm_weights():
    """Verifies that NaN or Infinity in MCDM weights are rejected."""
    resp = client.post("/api/v1/recommendations", json={
        "commodity_name": "Strawberry",
        "storage_conditions": {
            "storage_temperature_c": 4.0,
            "ambient_rh_percent": 90.0,
            "target_shelf_life_days": 7.0
        },
        "weights": {
            "shelf_life_weight": "nan",
            "barrier_performance_weight": 0.25,
            "sustainability_weight": 0.25,
            "cost_efficiency_weight": 0.15
        }
    })
    assert resp.status_code == 422


# -----------------------------------------------------------------------------
# 6. Recommendation Audit History & Single Record Retrieval (Section 11, 12)
# -----------------------------------------------------------------------------

def test_m5_recommendation_history_persistence_and_lookup():
    """
    Submits a recommendation, verifies it appears in /recommendations/history,
    and checks that /recommendations/{id} returns the complete audit record.
    """
    trace_id = f"trace-audit-{uuid.uuid4().hex[:8]}"
    post_res = client.post(
        "/api/v1/recommendations",
        headers={"X-Request-ID": trace_id},
        json={
            "commodity_name": "Strawberry",
            "storage_conditions": {
                "storage_temperature_c": 4.0,
                "ambient_rh_percent": 90.0,
                "target_shelf_life_days": 7.0
            }
        }
    )
    assert post_res.status_code == 200
    rec_data = post_res.json()
    assert rec_data["request_id"] == trace_id

    # Check history endpoint
    hist_res = client.get("/api/v1/recommendations/history?limit=10")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) > 0
    # The most recent recommendation should be first
    latest = history[0]
    assert latest["request_id"] == trace_id
    assert latest["commodity_name"] == "Strawberry"
    assert latest["recommendation_status"] == "AVAILABLE_WITHOUT_ML"
    assert latest["ml_status"] == "INSUFFICIENT_VERIFIED_DATA"

    # Check single recommendation retrieval by ID
    detail_res = client.get(f"/api/v1/recommendations/{trace_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["request_id"] == trace_id
    assert detail["primary_recommendation"]["name"] == rec_data["primary_recommendation"]["name"]
    assert detail["dataset_version"] == "1.0.0-m3"
    assert detail["rule_engine_version"] == "m2.0.0"
    assert detail["topsis_configuration_version"] == "m4.0.0"


# -----------------------------------------------------------------------------
# 7. Catalog Single-Item Lookups (Section 29, 30)
# -----------------------------------------------------------------------------

def test_m5_catalog_material_detail_lookup():
    """Verifies that /materials/{code} returns full ASTM barrier and polymer data."""
    resp = client.get("/api/v1/materials/PET-25")
    assert resp.status_code == 200
    mat = resp.json()
    assert mat["code"] == "PET-25"
    assert "Polyethylene Terephthalate" in mat["name"]
    assert mat["polymer_type"] == "PET"
    assert mat["thickness_micron"] == 25.0
    assert mat["otr_cc_m2_day_atm"] == 55.0
    assert mat["wvtr_g_m2_day"] == 15.5
    assert mat["food_contact_certified"] is True


def test_m5_catalog_commodity_detail_lookup():
    """Verifies that /commodities/{name} returns full physiological respiration data."""
    resp = client.get("/api/v1/commodities/Strawberry")
    assert resp.status_code == 200
    com = resp.json()
    assert com["name"] == "Strawberry"
    assert com["category"] == "FRUIT"
    assert com["respiration_rate_mg_co2_kg_hr"] in (12.0, 22.0)
    assert com["optimal_temperature_min_c"] == 0.0

