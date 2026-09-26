from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Food Packaging Material Recommendation",
    description=(
        "Receives commodity characteristics, cold-chain distribution parameters, "
        "and multi-attribute weights. In Milestone M0, this returns an explicit, structured "
        "architecture response without fabricating ML predictions or synthetic recommendations."
    )
)
def create_recommendation(
    payload: RecommendationRequest,
):
    """
    Submits packaging criteria to the pipeline.
    In Milestone M0, validates schema and returns structured pending-engines status.
    """
    service = RecommendationService()
    return service.generate_recommendation(payload)
