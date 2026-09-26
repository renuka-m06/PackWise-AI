from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """
    Standard health check response.
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
