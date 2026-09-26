import os
from app.main import app


def test_system_routes_registered():
    """Verify core routes are registered in FastAPI."""
    routes = [route.path for route in app.routes]
    assert "/api/v1/health" in routes
    assert "/api/v1/recommendations" in routes
    assert "/api/v1/commodities" in routes
    assert "/api/v1/materials" in routes


def test_frontend_dist_artifact_exists():
    """Verify frontend production build artifact is generated."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dist_index = os.path.join(project_root, "frontend", "dist", "index.html")
    assert os.path.exists(dist_index), "Frontend dist/index.html not found. Run 'npm run build' in frontend/."
