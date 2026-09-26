from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CommodityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    scientific_name: str | None = Field(default=None, max_length=150)
    category: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    respiration_rate_mg_co2_kg_hr: float | None = Field(default=None, ge=0.0)
    optimal_temperature_min_c: float = Field(default=4.0)
    optimal_temperature_max_c: float = Field(default=8.0)
    optimal_rh_min_percent: float = Field(default=85.0, ge=0.0, le=100.0)
    optimal_rh_max_percent: float = Field(default=95.0, ge=0.0, le=100.0)
    water_activity_aw: float | None = Field(default=None, ge=0.0, le=1.0)
    moisture_sensitive: bool = False
    oxygen_sensitive: bool = False
    ethylene_sensitive: bool = False
    light_sensitive: bool = False
    target_shelf_life_unpacked_days: int | None = Field(default=None, ge=1)


class CommodityCreate(CommodityBase):
    pass


class CommodityResponse(CommodityBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
