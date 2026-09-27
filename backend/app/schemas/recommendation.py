import math
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, field_validator
from app.schemas.storage_condition import StorageConditionBase
from app.schemas.material import PackagingMaterialResponse
from app.schemas.map_composition import MAPCompositionResponse


class RecommendationConstraints(BaseModel):
    prefer_biodegradable: bool = Field(default=False, description="Prioritize biodegradable materials")
    strict_food_contact_grade: bool = Field(default=True, description="Enforce certified food contact safety")
    max_acceptable_cost_index: Optional[float] = Field(default=None, gt=0.0, description="Cost index ceiling")
    require_high_moisture_barrier: bool = Field(default=False)
    require_high_oxygen_barrier: bool = Field(default=False)

    @field_validator("max_acceptable_cost_index", mode="before")
    @classmethod
    def validate_cost_index(cls, v):
        if v is not None:
            val = float(v)
            if not math.isfinite(val):
                raise ValueError("max_acceptable_cost_index must be a finite number")
            return val
        return v


class MCDMWeights(BaseModel):
    shelf_life_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    barrier_performance_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    sustainability_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    cost_efficiency_weight: float = Field(default=0.15, ge=0.0, le=1.0)

    @field_validator(
        "shelf_life_weight",
        "barrier_performance_weight",
        "sustainability_weight",
        "cost_efficiency_weight",
        mode="before"
    )
    @classmethod
    def validate_finite_weight(cls, v):
        val = float(v)
        if not math.isfinite(val):
            raise ValueError("Weights must be finite numbers (NaN and Infinity are prohibited)")
        if val < 0.0 or val > 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        return val

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

    @field_validator("commodity_name", mode="before")
    @classmethod
    def sanitize_commodity_name(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("commodity_name cannot be empty or pure whitespace")
        return v.strip()


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
    otr_cc_m2_day_atm: Optional[float] = None
    wvtr_g_m2_day: Optional[float] = None
    thickness_micron: Optional[float] = None
    cost_index_relative: Optional[float] = None
    is_biodegradable: Optional[bool] = None
    recyclability_code: Optional[int] = None


class RecommendationResponse(BaseModel):
    """
    Contract schema for packaging recommendations (Milestone M4).
    Provides explicit visibility into deterministic rule, ML, and MCDM stages,
    along with full evidence traces, alternative candidates, and version provenance.
    """
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="PENDING_ENGINES", description="Pipeline status: PENDING_ENGINES, COMPLETED, FILTERED_OUT")
    rule_engine_status: str = Field(default="COMPLETED", description="Rule engine status: COMPLETED, NOT_RUN")
    ml_status: str = Field(default="INSUFFICIENT_VERIFIED_DATA", description="ML model status: INSUFFICIENT_VERIFIED_DATA, VALIDATED, NOT_AVAILABLE")
    topsis_status: str = Field(default="COMPLETED", description="TOPSIS MCDM status: COMPLETED, NOT_RUN, SINGLE_CANDIDATE, INSUFFICIENT_DATA")
    recommendation_status: str = Field(default="AVAILABLE_WITHOUT_ML", description="Recommendation status: AVAILABLE, AVAILABLE_WITHOUT_ML, DISARMED_UNVERIFIED, NO_ELIGIBLE_MATERIAL, INSUFFICIENT_DATA")
    message: str = Field(..., description="Status explanation regarding model & empirical data readiness")
    recommended_material: Optional[PackagingMaterialResponse] = None
    primary_recommendation: Optional[PackagingMaterialResponse] = None
    alternative_materials: List[PackagingMaterialResponse] = Field(default_factory=list)
    suggested_map: Optional[MAPCompositionResponse] = None
    candidate_rankings: List[MaterialScoreResponse] = Field(default_factory=list)
    applied_rules: List[RuleFilterResult] = Field(default_factory=list)
    evidence_graph: List[dict] = Field(default_factory=list)
    explanation: Optional[str] = None
    dataset_version: str = Field(default="1.0.0-m3")
    rule_engine_version: str = Field(default="m2.0.0")
    topsis_configuration_version: str = Field(default="m4.0.0")
    ml_model_version: Optional[str] = None
    rejection_summary: Optional[dict] = None
    audit_metadata: Optional[dict] = None


class RecommendationHistoryItem(BaseModel):
    request_id: str
    timestamp: datetime
    commodity_name: str
    storage_temperature_c: float
    ambient_rh_percent: float
    target_shelf_life_days: float
    primary_material_name: Optional[str] = None
    primary_polymer_type: Optional[str] = None
    topsis_score: Optional[float] = None
    recommendation_status: str
    rule_engine_status: str
    ml_status: str
