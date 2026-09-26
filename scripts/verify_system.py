#!/usr/bin/env python3
"""
PackWise AI - Milestone M0 Verification Script
Verifies:
1. Backend imports and route registration
2. Zero hardcoded secrets / credentials in source
3. Zero fake/synthetic model claims
4. Pydantic schema integrity
5. TOPSIS mathematical engine accuracy
6. Rule filter engine execution
"""
import sys
import os
import re

# Ensure standard output handles encoding gracefully
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend directory is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "backend"))

def main():
    print("=" * 60)
    print("PackWise AI - Verification Suite (Milestone M0)")
    print("=" * 60)

    # 1. Verify Imports
    print("[1/6] Verifying backend imports...")
    try:
        from app.main import app
        from app.core.config import settings
        from app.engines.ranking.topsis import TOPSISDecisionEngine
        from app.engines.rules.filter_engine import RuleFilterEngine
        from app.schemas.recommendation import RecommendationRequest
        from app.schemas.health import HealthCheckResponse
        print("  [PASS] Backend modules, schemas, and engines imported cleanly.")
    except Exception as e:
        print(f"  [FAIL] Import failure: {e}")
        return 1

    # 2. Check Health Endpoint Contract
    print("[2/6] Verifying health check contract...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy", f"Expected 'healthy', got {data['status']}"
    assert data["service"] == "foodpack-api", f"Expected 'foodpack-api', got {data['service']}"
    print(f"  [PASS] /api/v1/health returned exact contract: {data}")

    # 3. Check TOPSIS Engine
    print("[3/6] Verifying TOPSIS MCDM mathematical engine...")
    import numpy as np
    matrix = np.array([[10.0, 1.0], [5.0, 2.0]])
    weights = np.array([0.7, 0.3])
    mask = np.array([True, False])
    ranks = TOPSISDecisionEngine.rank_candidates(matrix, weights, mask, ["opt1", "opt2"])
    assert len(ranks) == 2
    assert ranks[0]["id"] == "opt1"
    assert ranks[0]["rank"] == 1
    print("  [PASS] TOPSIS vector normalization and ranking verified.")

    # 4. Check Rule Screening Engine
    print("[4/6] Verifying Rule Screening Engine...")
    rule_engine = RuleFilterEngine()
    passed, rejected, audit = rule_engine.screen_materials(
        commodity={"moisture_sensitive": True},
        materials=[
            {"name": "Safe Foil", "wvtr_g_m2_day": 2.0, "food_contact_certified": True},
            {"name": "Leaky Film", "wvtr_g_m2_day": 85.0, "food_contact_certified": True}
        ],
        storage={"ambient_rh_percent": 90.0}
    )
    assert len(passed) == 1
    assert passed[0]["name"] == "Safe Foil"
    assert len(rejected) == 1
    print("  [PASS] Rule-based filtering screening verified.")

    # 5. Check Recommendations Endpoint Contract (Zero Fake Data)
    print("[5/6] Verifying zero fake recommendations policy on POST /api/v1/recommendations...")
    res = client.post("/api/v1/recommendations", json={
        "commodity_name": "Fresh Cut Strawberries",
        "storage_conditions": {
            "storage_temperature_c": 4.0,
            "ambient_rh_percent": 85.0,
            "target_shelf_life_days": 14
        }
    })
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "PENDING_ENGINES"
    assert res_data["recommended_material"] is None
    assert len(res_data["candidate_rankings"]) == 0
    print("  [PASS] Recommendations endpoint contract verified: Strict zero fake-recommendation policy enforced.")

    # 6. Verify No Hardcoded Passwords / Secrets
    print("[6/6] Verifying absence of hardcoded secret tokens...")
    forbidden_patterns = [
        re.compile(r"api_key\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", re.IGNORECASE),
        re.compile(r"secret_key\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", re.IGNORECASE),
    ]
    scan_count = 0
    for root, _, files in os.walk(os.path.join(project_root, "backend", "app")):
        for file in files:
            if file.endswith(".py"):
                scan_count += 1
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    for pat in forbidden_patterns:
                        assert not pat.search(content), f"Potential secret found in {file}"
    print(f"  [PASS] Scanned {scan_count} source files. No hardcoded API keys/secrets discovered.")

    print("\n" + "=" * 60)
    print("ALL MILESTONE M0 FOUNDATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
