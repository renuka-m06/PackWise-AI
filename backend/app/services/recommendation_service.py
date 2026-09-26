from sqlalchemy.orm import Session
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.engines.recommendation.orchestrator import RecommendationOrchestrator


class RecommendationService:
    """
    Application service managing the recommendation lifecycle.
    Keeps API controllers free of orchestration and database logic.
    """
    def __init__(self, db: Session | None = None):
        self.db = db
        self.orchestrator = RecommendationOrchestrator()

    def generate_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Executes pipeline orchestration. In Milestone M0, returns formal status
        confirming contract schema validity without fabricating recommendations.
        """
        return self.orchestrator.process_recommendation_request(request)
