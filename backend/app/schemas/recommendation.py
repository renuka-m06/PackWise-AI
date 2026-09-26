from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from app.schemas.storage_condition import StorageConditionBase
from app.schemas.material import PackagingMaterialResponse
from app.schemas.map_composition import MAPCompositionResponse


class RecommendationConstraints(BaseModel):
    prefer_biodegradable: bool = Field(default=False, description="Prioritize biodegradable materials")
    strict_food_contact_grade: bool = Field(default=True, description="Enforce certified food contact safety")
    max_acceptable_cost_index: Optional[float] = Field(default=None, gt=0.0, description="Cost index ceiling")
    require_high_moisture_barrier: bool = Field(default=False)
    require_high_oxygen_barrier: bool = Field(default=False)


class MCDMWeights(BaseModel):
    shelf_life_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    barrier_performance_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    sustainability_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    cost_efficiency_weight: float = Field(default=0.15, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_weights(self):
        total = (
            self.shelf_life_weight +
            self.barrier_performance_weight +
            self.sustainability_weight +
            self.cost_efficiency_weight
        )
        if abs(total - 1.0) > 0.05:
            # Normalize automatically if not exactly 1.0
            scale = 1.0 / total if total > 0 else 1.0
            self.shelf_life_weight = round(self.shelf_life_weight * scale, 3)
            self.barrier_performance_weight = round(self.barrier_performance_weight * scale, 3)
            self.sustainability_weight = round(self.sustainability_weight * scale, 3)
            self.cost_efficiency_weight = round(self.cost_efficiency_weight * scale, 3)
        return self


class RecommendationRequest(BaseModel):
    """
    Input payload for requesting a food packaging material recommendation.
    """
    commodity_name: str = Field(..., min_length=2, max_length=120, description="Target food commodity")
    commodity_category: Optional[str] = Field(default=None, description="Produce category if known")
    storage_conditions: StorageConditionBase
    constraints: RecommendationConstraints = Field(default_factory=RecommendationConstraints)
    weights: MCDMWeights = Field(default_factory=MCDMWeights)


class RuleFilterResult(BaseModel):
    rule_name: str
    passed: bool
    explanation: str


class MaterialScoreResponse(BaseModel):
    material_id: str
    material_name: str
    polymer_type: str
    topsis_score: float
    rank: int
    barrier_score: float
    sustainability_score: float
    cost_score: float


class RecommendationResponse(BaseModel):
    """
    Contract schema for packaging recommendations.
    In Milestone M0, returns status='PENDING_ENGINES' with explicit architectural notice.
    """
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="PENDING_ENGINES", description="Pipeline status: PENDING_ENGINES, COMPLETED, FILTERED_OUT")
    message: str = Field(..., description="Status explanation regarding model & empirical data readiness")
    recommended_material: Optional[PackagingMaterialResponse] = None
    suggested_map: Optional[MAPCompositionResponse] = None
    candidate_rankings: List[MaterialScoreResponse] = Field(default_factory=list)
    applied_rules: List[RuleFilterResult] = Field(default_factory=list)
    explanation: Optional[str] = None
