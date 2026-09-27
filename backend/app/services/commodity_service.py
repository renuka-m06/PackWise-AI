import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.commodity import Commodity
from app.schemas.commodity import CommodityCreate, CommodityResponse
from app.core.exceptions import ResourceNotFoundException
from app.db.empirical_data import get_verified_commodities, get_verified_commodity


class CommodityService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def _convert_empirical_to_response(self, c: dict) -> CommodityResponse:
        det_id = uuid.uuid5(uuid.NAMESPACE_DNS, c["name"])
        now = datetime.now(timezone.utc)
        return CommodityResponse(
            id=det_id,
            name=c["name"],
            scientific_name=c.get("scientific_name"),
            category=c.get("category", "GENERAL"),
            description=f"Verified empirical postharvest commodity profile ({c.get('category')}).",
            respiration_rate_mg_co2_kg_hr=c.get("respiration_rate_mg_co2_kg_hr"),
            optimal_temperature_min_c=c.get("optimal_temperature_min_c", 0.0),
            optimal_temperature_max_c=c.get("optimal_temperature_max_c", 4.0),
            optimal_rh_min_percent=c.get("optimal_rh_min_percent", 85.0),
            optimal_rh_max_percent=c.get("optimal_rh_max_percent", 95.0),
            water_activity_aw=c.get("water_activity_aw"),
            moisture_sensitive=c.get("moisture_sensitive", False),
            oxygen_sensitive=c.get("oxygen_sensitive", False),
            ethylene_sensitive=c.get("ethylene_sensitive", False),
            light_sensitive=c.get("light_sensitive", False),
            target_shelf_life_unpacked_days=7,
            created_at=now,
            updated_at=now
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CommodityResponse]:
        if self.db is not None:
            try:
                stmt = select(Commodity).offset(skip).limit(limit)
                db_results = list(self.db.scalars(stmt).all())
                if db_results:
                    return [CommodityResponse.model_validate(r) for r in db_results]
            except Exception:
                pass

        # Empirical data fallback
        empirical = list(get_verified_commodities().values())
        sliced = empirical[skip : skip + limit]
        return [self._convert_empirical_to_response(c) for c in sliced]

    def get_by_name(self, name: str) -> Optional[CommodityResponse]:
        if self.db is not None:
            try:
                stmt = select(Commodity).where(Commodity.name.ilike(name))
                db_commodity = self.db.scalars(stmt).first()
                if db_commodity:
                    return CommodityResponse.model_validate(db_commodity)
            except Exception:
                pass

        c = get_verified_commodity(name)
        if c:
            return self._convert_empirical_to_response(c)
        return None

    def get_by_id_or_name(self, identifier: str) -> CommodityResponse:
        c = self.get_by_name(identifier)
        if c:
            return c

        if self.db is not None:
            try:
                parsed_uuid = uuid.UUID(identifier)
                db_commodity = self.db.get(Commodity, parsed_uuid)
                if db_commodity:
                    return CommodityResponse.model_validate(db_commodity)
            except Exception:
                pass

        for com in get_verified_commodities().values():
            det_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, com["name"]))
            if det_id.lower() == identifier.lower():
                return self._convert_empirical_to_response(com)

        raise ResourceNotFoundException("Commodity", identifier)
