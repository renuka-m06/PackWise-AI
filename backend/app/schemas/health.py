from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """
    Standard health check response verifying process liveness.
    Exact contract:
    {
      "status": "healthy",
      "service": "foodpack-api"
    }
    """
    status: str = Field(default="healthy", description="Service health state")
    service: str = Field(default="foodpack-api", description="Service identifier")
    version: str | None = Field(default=None, description="Current release version")
    environment: str | None = Field(default=None, description="Runtime environment")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of diagnostic check")


class ComponentReadiness(BaseModel):
    status: str = Field(..., description="READY, OPERATIONAL, DATA_GATED, DEGRADED, OFFLINE")
    message: str = Field(..., description="Diagnostic summary of component condition")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Component metadata or counters")


class ReadinessCheckResponse(BaseModel):
    """
    Production readiness response assessing subsystem dependencies:
    API, Database, Rule Engine, TOPSIS MCDM, Empirical Dataset, and ML Gate.
    """
    status: str = Field(default="READY", description="Overall readiness: READY, DEGRADED, NOT_READY")
    service: str = Field(default="foodpack-api", description="Service identifier")
    version: str = Field(..., description="System release version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    components: Dict[str, ComponentReadiness] = Field(..., description="Detailed status breakdown per subsystem")
