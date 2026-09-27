from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.schemas.recommendation import (
    RecommendationRequest, 
    RecommendationResponse,
    RecommendationHistoryItem
)
from app.services.recommendation_service import RecommendationService
from app.db.session import get_db_optional

router = APIRouter()


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Food Packaging Material Recommendation",
    description=(
        "Executes the authoritative 20-stage scientific decision pipeline: "
        "commodity resolution, packaging requirements, deterministic rule screening, "
        "hard constraint elimination, TOPSIS multi-criteria ranking, MAP selection, "
        "evidence graph compilation, and ML status reporting."
    )
)
def create_recommendation(
    payload: RecommendationRequest,
    request: Request,
    db: Optional[Session] = Depends(get_db_optional)
):
    """
    Submits packaging criteria to the pipeline.
    Preserves request-id traceability and persists audit records.
    """
    request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")
    service = RecommendationService(db=db)
    return service.generate_recommendation(payload, request_id=request_id)


@router.get(
    "/recommendations/history",
    response_model=List[RecommendationHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="List Recommendation Audit History",
    description="Returns previous recommendation runs with timestamp, inputs, primary recommendation, and status."
)
def get_recommendation_history(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page size limit"),
    db: Optional[Session] = Depends(get_db_optional)
):
    service = RecommendationService(db=db)
    return service.get_history(skip=skip, limit=limit)


@router.get(
    "/recommendations/{request_id}",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Detailed Recommendation Record",
    description="Returns complete recommendation response, rankings, applied rules, and evidence graph by request_id."
)
def get_recommendation_by_id(
    request_id: str,
    db: Optional[Session] = Depends(get_db_optional)
):
    service = RecommendationService(db=db)
    return service.get_by_id(request_id)
