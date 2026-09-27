from fastapi.testclient import TestClient


def test_recommendation_contract_unverified_commodity_disarmed(client: TestClient):
    """
    Verify POST /api/v1/recommendations validates schema and returns
    structured disarmed status (PENDING_ENGINES) for unverified commodities.
    """
    unverified_payload = {
        "commodity_name": "Unverified Lab-Grown Hybrid",
        "commodity_category": "FRUIT",
        "storage_conditions": {
            "storage_temperature_c": 4.0,
            "ambient_rh_percent": 85.0,
            "target_shelf_life_days": 14,
            "cold_chain_reliability": "STRICT_COLD_CHAIN"
        }
    }

    response = client.post("/api/v1/recommendations", json=unverified_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "PENDING_ENGINES"
    assert data["recommended_material"] is None
    assert data["suggested_map"] is None
    assert len(data["candidate_rankings"]) == 0
    assert "request_id" in data


def test_recommendation_m2_verified_flow(client: TestClient):
    """
    Verify POST /api/v1/recommendations executes the deterministic M2 pipeline
    for a verified commodity (Apple) and returns TOPSIS-ranked candidates.
    """
    valid_payload = {
        "commodity_name": "Apple",
        "commodity_category": "FRUIT",
        "storage_conditions": {
            "storage_temperature_c": 2.0,
            "ambient_rh_percent": 90.0,
            "target_shelf_life_days": 30,
            "cold_chain_reliability": "STRICT_COLD_CHAIN"
        },
        "constraints": {
            "prefer_biodegradable": False,
            "strict_food_contact_grade": True,
            "require_high_moisture_barrier": False,
            "require_high_oxygen_barrier": False
        },
        "weights": {
            "shelf_life_weight": 0.4,
            "barrier_performance_weight": 0.2,
            "sustainability_weight": 0.2,
            "cost_efficiency_weight": 0.2
        }
    }

    response = client.post("/api/v1/recommendations", json=valid_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["recommended_material"] is not None
    assert len(data["candidate_rankings"]) > 0
    assert len(data["applied_rules"]) > 0
    assert "ASTM" in data["explanation"]


def test_recommendation_m2_impossible_constraints_returns_no_eligible(client: TestClient):
    """
    Verify that when impossible constraints eliminate all materials, the system
    returns NO_ELIGIBLE_MATERIAL instead of fabricating a recommendation.
    """
    impossible_payload = {
        "commodity_name": "Strawberry",
        "commodity_category": "FRUIT",
        "storage_conditions": {
            "storage_temperature_c": 4.0,
            "ambient_rh_percent": 95.0,
            "target_shelf_life_days": 14,
            "cold_chain_reliability": "STRICT_COLD_CHAIN"
        },
        "constraints": {
            "prefer_biodegradable": True,
            "strict_food_contact_grade": True,
            "require_high_moisture_barrier": True,
            "require_high_oxygen_barrier": True
        }
    }

    response = client.post("/api/v1/recommendations", json=impossible_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "NO_ELIGIBLE_MATERIAL"
    assert data["recommended_material"] is None
    assert len(data["candidate_rankings"]) == 0


def test_recommendation_invalid_payload_fails(client: TestClient):
    """
    Verify invalid payloads (e.g. impossible storage temperature or invalid RH)
    fail validation with HTTP 422.
    """
    invalid_payload = {
        "commodity_name": "",  # Min length 2 required
        "storage_conditions": {
            "storage_temperature_c": 200.0,  # Exceeds maximum 50.0
            "ambient_rh_percent": 150.0,    # Exceeds maximum 100.0
            "target_shelf_life_days": 0     # Min 1 required
        }
    }

    response = client.post("/api/v1/recommendations", json=invalid_payload)
    assert response.status_code == 422
