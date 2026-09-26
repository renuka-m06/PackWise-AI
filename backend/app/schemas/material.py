from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PackagingMaterialBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=50)
    polymer_type: str = Field(..., min_length=2, max_length=60)
    description: str | None = None
    thickness_micron: float = Field(default=25.0, gt=0.0)
    otr_cc_m2_day_atm: float = Field(..., ge=0.0, description="Oxygen Transmission Rate ASTM D3985")
    wvtr_g_m2_day: float = Field(..., ge=0.0, description="Water Vapor Transmission Rate ASTM F1249")
    tensile_strength_mpa: float | None = Field(default=None, ge=0.0)
    seal_strength_n_15mm: float | None = Field(default=None, ge=0.0)
    transparency_pct: float | None = Field(default=None, ge=0.0, le=100.0)
    is_biodegradable: bool = False
    biodegradation_standard: str | None = None
    recyclability_code: int = Field(default=7, ge=1, le=7)
    cost_index_relative: float = Field(default=1.0, gt=0.0)
    carbon_footprint_kg_co2_per_kg: float | None = Field(default=None, ge=0.0)
    food_contact_certified: bool = True


class PackagingMaterialCreate(PackagingMaterialBase):
    pass


class PackagingMaterialResponse(PackagingMaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
