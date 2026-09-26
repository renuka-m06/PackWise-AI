from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_v1_health_flow():
    """
    Integration test verifying the exact API contract for /api/v1/health.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "foodpack-api"


def test_api_v1_recommendation_flow():
    """
    Integration test verifying that /api/v1/recommendations accepts standard
    commodity payload and returns status PENDING_ENGINES with zero fake recommendations.
    """
    payload = {
        "commodity_name": "Broccoli",
        "commodity_category": "VEGETABLE",
        "storage_conditions": {
            "storage_temperature_c": 1.0,
            "ambient_rh_percent": 95.0,
            "target_shelf_life_days": 21,
            "cold_chain_reliability": "STRICT_COLD_CHAIN"
        },
        "constraints": {
            "prefer_biodegradable": False,
            "strict_food_contact_grade": True,
            "require_high_moisture_barrier": True,
            "require_high_oxygen_barrier": False
        },
        "weights": {
            "shelf_life_weight": 0.4,
            "barrier_performance_weight": 0.2,
            "sustainability_weight": 0.2,
            "cost_efficiency_weight": 0.2
        }
    }

    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING_ENGINES"
    assert data["recommended_material"] is None
    assert len(data["candidate_rankings"]) == 0
