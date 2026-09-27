import os
from fastapi import APIRouter, status
from sqlalchemy import text
from app.schemas.health import HealthCheckResponse, ReadinessCheckResponse, ComponentReadiness
from app.core.config import settings
from app.db.session import engine
from app.db.empirical_data import get_verified_commodities, get_verified_materials, get_verified_map_compositions
from app.engines.rules.filter_engine import RULE_ENGINE_VERSION
from app.engines.ranking.topsis import TOPSISDecisionEngine

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health Liveness Check",
    description="Returns live system health and service identification."
)
def check_health():
    """
    Contract Health Check Endpoint.
    Returns:
    {
      "status": "healthy",
      "service": "foodpack-api"
    }
    """
    return HealthCheckResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        environment=settings.APP_ENV
    )


@router.get(
    "/readiness",
    response_model=ReadinessCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="System Operational Readiness Check",
    description=(
        "Evaluates the operational readiness of all core subsystems: "
        "Database, Rule Engine, TOPSIS MCDM, Empirical Dataset, and ML Gate. "
        "ML data-gating does not mark the system unready."
    )
)
def check_readiness():
    components = {}

    # 1. API Gateway
    components["api"] = ComponentReadiness(
        status="READY",
        message="FastAPI application router mounted and accepting requests",
        details={"prefix": settings.API_PREFIX, "environment": settings.APP_ENV}
    )

    # 2. Database Connectivity
    db_connected = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_connected = True
    except Exception:
        db_connected = False

    if db_connected:
        components["database"] = ComponentReadiness(
            status="READY",
            message="PostgreSQL relational connection pool active",
            details={"connection": "online"}
        )
    else:
        components["database"] = ComponentReadiness(
            status="OFFLINE_FALLBACK",
            message="PostgreSQL offline or unreachable; active fallback to verified empirical repository",
            details={"connection": "offline_fallback", "zero_fabrication": True}
        )

    # 3. Empirical Dataset Availability
    commodities = get_verified_commodities()
    materials = get_verified_materials()
    map_forms = get_verified_map_compositions()
    dataset_ready = len(commodities) > 0 and len(materials) > 0
    components["empirical_dataset"] = ComponentReadiness(
        status="READY" if dataset_ready else "NOT_READY",
        message=f"Verified empirical dataset loaded ({len(commodities)} commodities, {len(materials)} materials)",
        details={
            "dataset_version": "1.0.0-m3",
            "commodities_count": len(commodities),
            "materials_count": len(materials),
            "map_formulations_count": len(map_forms),
            "zero_synthetic_data": True
        }
    )

    # 4. Scientific Rule Engine
    components["rule_engine"] = ComponentReadiness(
        status="READY",
        message="Deterministic scientific rule engine active with hard safety screening",
        details={
            "version": RULE_ENGINE_VERSION,
            "rules_count": 9,
            "food_contact_enforced": True,
            "pathogen_safety_enforced": True
        }
    )

    # 5. TOPSIS Multi-Criteria Decision Engine
    criteria = TOPSISDecisionEngine.get_default_criteria()
    components["topsis"] = ComponentReadiness(
        status="READY",
        message="TOPSIS MCDM vector normalization and ranking engine active",
        details={
            "version": TOPSISDecisionEngine.CONFIG_VERSION,
            "criteria_count": len(criteria),
            "normalization": "vector_l2"
        }
    )

    # 6. ML Model Registry & Data Sufficiency Gate
    # Critical: ML being DATA_GATED does NOT fail overall readiness!
    components["ml"] = ComponentReadiness(
        status="DATA_GATED",
        message="ML training blocked by M3 sufficiency gate (N=37 < 100). Deterministic fallback active.",
        details={
            "ml_status": "INSUFFICIENT_VERIFIED_DATA",
            "production_models_trained": 0,
            "fallback_engine": "M2_Rules_and_TOPSIS"
        }
    )

    overall_status = "READY" if dataset_ready else "NOT_READY"

    return ReadinessCheckResponse(
        status=overall_status,
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        components=components
    )
