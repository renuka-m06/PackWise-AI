from fastapi import APIRouter, status
from app.schemas.health import HealthCheckResponse
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic Check",
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
