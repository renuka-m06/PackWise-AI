from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    """
    Verify GET /api/v1/health returns expected contract:
    {
      "status": "healthy",
      "service": "foodpack-api"
    }
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "foodpack-api"


def test_root_endpoint(client: TestClient):
    """
    Verify GET / returns service descriptor.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "foodpack-api"
