from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator


class MAPCompositionBase(BaseModel):
    composition_name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    oxygen_pct: float = Field(..., ge=0.0, le=100.0)
    carbon_dioxide_pct: float = Field(..., ge=0.0, le=100.0)
    nitrogen_pct: float = Field(..., ge=0.0, le=100.0)
    target_application: str | None = None

    @model_validator(mode="after")
    def validate_gas_sum(self):
        total = self.oxygen_pct + self.carbon_dioxide_pct + self.nitrogen_pct
        if abs(total - 100.0) > 1.0:
            raise ValueError(f"Gas volume percentages must sum to ~100%, got {total:.2f}%")
        return self


class MAPCompositionResponse(MAPCompositionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
