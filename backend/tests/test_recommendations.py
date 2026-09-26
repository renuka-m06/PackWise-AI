from fastapi.testclient import TestClient


def test_recommendation_contract_validation(client: TestClient):
    """
    Verify POST /api/v1/recommendations validates schema and returns
    structured M0 response without generating fake recommendations.
    """
    valid_payload = {
        "commodity_name": "Fresh Strawberries",
        "commodity_category": "FRUIT",
        "storage_conditions": {
            "storage_temperature_c": 4.0,
            "ambient_rh_percent": 85.0,
            "target_shelf_life_days": 14,
            "cold_chain_reliability": "STRICT_COLD_CHAIN"
        },
        "constraints": {
            "prefer_biodegradable": True,
            "strict_food_contact_grade": True,
            "require_high_moisture_barrier": True,
            "require_high_oxygen_barrier": True
        },
        "weights": {
            "shelf_life_weight": 0.4,
            "barrier_performance_weight": 0.3,
            "sustainability_weight": 0.2,
            "cost_efficiency_weight": 0.1
        }
    }

    response = client.post("/api/v1/recommendations", json=valid_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "PENDING_ENGINES"
    assert "M0" in data["message"]
    # Verify no fake recommendation is returned
    assert data["recommended_material"] is None
    assert data["suggested_map"] is None
    assert len(data["candidate_rankings"]) == 0
    assert "request_id" in data


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
