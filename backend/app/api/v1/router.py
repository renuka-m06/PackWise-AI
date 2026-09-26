from fastapi import APIRouter
from app.api.v1.endpoints import health, recommendations, catalog

api_router = APIRouter()

# Health Check Endpoint
api_router.include_router(health.router, tags=["Health"])

# Packaging Recommendation Pipeline
api_router.include_router(recommendations.router, tags=["Recommendations"])

# Material & Commodity Catalog
api_router.include_router(catalog.router, tags=["Catalog"])
