import math
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ColdChainRegime(str, Enum):
    STRICT_COLD_CHAIN = "STRICT_COLD_CHAIN"
    INTERMITTENT = "INTERMITTENT"
    AMBIENT = "AMBIENT"


class StorageConditionBase(BaseModel):
    storage_temperature_c: float = Field(..., ge=-30.0, le=50.0, description="Storage temperature in Celsius")
    ambient_rh_percent: float = Field(..., ge=0.0, le=100.0, description="Ambient relative humidity %")
    target_shelf_life_days: float = Field(..., ge=0.1, le=730.0, description="Target preservation shelf life in days")
    distribution_distance_km: float | None = Field(default=None, ge=0.0, description="Estimated distribution radius")
    cold_chain_reliability: ColdChainRegime = Field(default=ColdChainRegime.STRICT_COLD_CHAIN)

    @field_validator("storage_temperature_c", "ambient_rh_percent", "target_shelf_life_days", mode="before")
    @classmethod
    def validate_finite_numbers(cls, v: float) -> float:
        if v is None:
            return v
        try:
            val = float(v)
        except (ValueError, TypeError):
            raise ValueError(f"Numeric value expected, got {v}")
        if not math.isfinite(val):
            raise ValueError("Numeric value must be finite (NaN and Infinity are strictly prohibited)")
        return val
