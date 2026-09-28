from typing import List, Optional, Dict
from collections import OrderedDict
from datetime import datetime, timezone
import threading
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.schemas.recommendation import (
    RecommendationRequest, 
    RecommendationResponse,
    RecommendationHistoryItem
)
from app.engines.recommendation.orchestrator import RecommendationOrchestrator
from app.models.recommendation import RecommendationRecord
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import logger

# Thread-safe in-memory ring-buffer audit store (persists recommendations across request lifecycles)
_MAX_AUDIT_ENTRIES = 500
_AUDIT_STORE: OrderedDict[str, RecommendationResponse] = OrderedDict()
_AUDIT_LOCK = threading.Lock()


class RecommendationService:
    """
    Application service managing the recommendation lifecycle, persistence, and audit retrieval.
    Keeps API controllers free of orchestration and database logic.
    """
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.orchestrator = RecommendationOrchestrator()

    def generate_recommendation(
        self, 
        request: RecommendationRequest,
        request_id: Optional[str] = None
    ) -> RecommendationResponse:
        """
        Executes end-to-end recommendation pipeline and records audit history.
        """
        response = self.orchestrator.process_recommendation_request(request, request_id=request_id)

        # 1. Thread-safe in-memory audit persistence
        with _AUDIT_LOCK:
            _AUDIT_STORE[response.request_id] = response
            if len(_AUDIT_STORE) > _MAX_AUDIT_ENTRIES:
                _AUDIT_STORE.popitem(last=False)

        # 2. Database persistence if active connection exists
        if self.db is not None:
            try:
                summary_data = {
                    "request_id": response.request_id,
                    "status": response.rule_engine_status,
                    "eligible_count": len(response.alternative_materials) + (1 if response.primary_recommendation else 0),
                    "primary_name": response.primary_recommendation.name if response.primary_recommendation else None,
                    "primary_code": response.primary_recommendation.code if response.primary_recommendation else None,
                    "primary_polymer": response.primary_recommendation.polymer_type if response.primary_recommendation else None,
                    "recommendation_status": response.recommendation_status,
                    "rule_engine_status": response.rule_engine_status,
                    "ml_status": response.ml_status,
                }
                rec_model = RecommendationRecord(
                    commodity_name_input=request.commodity_name,
                    request_payload=request.model_dump(mode="json"),
                    rule_filtering_summary=summary_data,
                    topsis_scores={
                        "scores": [
                            {"material_id": c.material_id, "score": c.topsis_score, "rank": c.rank}
                            for c in response.candidate_rankings
                        ]
                    },
                    engine_version=f"{response.rule_engine_version}_{response.topsis_configuration_version}"
                )
                self.db.add(rec_model)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                logger.warning(f"Could not persist recommendation audit record to database: {e}")

        return response

    def get_history(self, skip: int = 0, limit: int = 50) -> List[RecommendationHistoryItem]:
        """
        Retrieves historical recommendation audit summaries, ordered newest first.
        Queries PostgreSQL if connected; falls back to in-memory audit store if offline.
        """
        if self.db is not None:
            try:
                stmt = select(RecommendationRecord).order_by(desc(RecommendationRecord.created_at)).offset(skip).limit(limit)
                db_records = list(self.db.scalars(stmt).all())
                if db_records:
                    db_items: List[RecommendationHistoryItem] = []
                    for rec in db_records:
                        payload = rec.request_payload or {}
                        storage = payload.get("storage_conditions", {})
                        summary = rec.rule_filtering_summary or {}
                        scores_dict = rec.topsis_scores or {}
                        scores_list = scores_dict.get("scores", [])
                        top_score = scores_list[0].get("score") if scores_list else None
                        
                        req_id = summary.get("request_id") or str(rec.id)
                        created_dt = rec.created_at
                        if isinstance(created_dt, datetime) and created_dt.tzinfo is None:
                            created_dt = created_dt.replace(tzinfo=timezone.utc)

                        db_items.append(
                            RecommendationHistoryItem(
                                request_id=req_id,
                                timestamp=created_dt if isinstance(created_dt, datetime) else datetime.now(timezone.utc),
                                commodity_name=rec.commodity_name_input,
                                storage_temperature_c=storage.get("storage_temperature_c", 4.0),
                                ambient_rh_percent=storage.get("ambient_rh_percent", 85.0),
                                target_shelf_life_days=storage.get("target_shelf_life_days", 7.0),
                                primary_material_name=summary.get("primary_name"),
                                primary_polymer_type=summary.get("primary_polymer"),
                                topsis_score=top_score,
                                recommendation_status=summary.get("recommendation_status", "AVAILABLE_WITHOUT_ML"),
                                rule_engine_status=summary.get("rule_engine_status", "COMPLETED"),
                                ml_status=summary.get("ml_status", "INSUFFICIENT_VERIFIED_DATA")
                            )
                        )
                    return db_items
            except Exception as e:
                logger.warning(f"Could not load recommendation history from database: {e}")

        # In-memory fallback
        history_items: List[RecommendationHistoryItem] = []

        with _AUDIT_LOCK:
            cached_responses = list(reversed(list(_AUDIT_STORE.values())))

        sliced = cached_responses[skip : skip + limit]

        for resp in sliced:
            storage_conditions = resp.audit_metadata.get("storage_conditions", {}) if resp.audit_metadata else {}
            temp_c = storage_conditions.get("storage_temperature_c", 4.0)
            rh_pct = storage_conditions.get("ambient_rh_percent", 85.0)
            days = storage_conditions.get("target_shelf_life_days", 7.0)

            primary_name = resp.primary_recommendation.name if resp.primary_recommendation else None
            primary_polymer = resp.primary_recommendation.polymer_type if resp.primary_recommendation else None
            topsis_score = resp.candidate_rankings[0].topsis_score if resp.candidate_rankings else None

            commodity_name = "Unknown"
            if resp.audit_metadata and "commodity_name" in resp.audit_metadata:
                commodity_name = resp.audit_metadata["commodity_name"]
            elif resp.applied_rules and len(resp.applied_rules) > 0:
                explanation = resp.applied_rules[0].explanation
                if "Commodity '" in explanation:
                    commodity_name = explanation.split("Commodity '")[1].split("'")[0]

            history_items.append(
                RecommendationHistoryItem(
                    request_id=resp.request_id,
                    timestamp=resp.timestamp,
                    commodity_name=commodity_name,
                    storage_temperature_c=temp_c,
                    ambient_rh_percent=rh_pct,
                    target_shelf_life_days=days,
                    primary_material_name=primary_name,
                    primary_polymer_type=primary_polymer,
                    topsis_score=topsis_score,
                    recommendation_status=resp.recommendation_status,
                    rule_engine_status=resp.rule_engine_status,
                    ml_status=resp.ml_status
                )
            )

        return history_items

    def get_by_id(self, request_id: str) -> RecommendationResponse:
        """
        Retrieves complete recommendation response payload by correlation request_id.
        """
        with _AUDIT_LOCK:
            if request_id in _AUDIT_STORE:
                return _AUDIT_STORE[request_id]

        raise ResourceNotFoundException("Recommendation", request_id)
