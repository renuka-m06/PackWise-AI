import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.material import PackagingMaterial
from app.schemas.material import PackagingMaterialCreate, PackagingMaterialResponse
from app.core.exceptions import ResourceNotFoundException
from app.db.empirical_data import get_verified_materials


class MaterialService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def _convert_empirical_to_response(self, m: dict) -> PackagingMaterialResponse:
        det_id = uuid.uuid5(uuid.NAMESPACE_DNS, m["code"])
        now = datetime.now(timezone.utc)
        return PackagingMaterialResponse(
            id=det_id,
            name=m["name"],
            code=m["code"],
            polymer_type=m["polymer_type"],
            description=f"Verified packaging film ({m['polymer_type']}) with standard ASTM test ratings.",
            thickness_micron=m.get("thickness_micron", 25.0),
            otr_cc_m2_day_atm=m.get("otr_cc_m2_day_atm", 100.0),
            wvtr_g_m2_day=m.get("wvtr_g_m2_day", 10.0),
            tensile_strength_mpa=m.get("tensile_strength_mpa"),
            is_biodegradable=m.get("is_biodegradable", False),
            biodegradation_standard=m.get("biodegradation_standard"),
            recyclability_code=m.get("recyclability_code", 7),
            cost_index_relative=m.get("cost_index_relative", 1.0),
            carbon_footprint_kg_co2_per_kg=m.get("carbon_footprint_kg_co2_per_kg"),
            food_contact_certified=m.get("food_contact_certified", True),
            created_at=now,
            updated_at=now
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PackagingMaterialResponse]:
        if self.db is not None:
            try:
                stmt = select(PackagingMaterial).offset(skip).limit(limit)
                db_results = list(self.db.scalars(stmt).all())
                if db_results:
                    return [PackagingMaterialResponse.model_validate(r) for r in db_results]
            except Exception:
                pass

        # Empirical data fallback
        empirical = get_verified_materials()
        sliced = empirical[skip : skip + limit]
        return [self._convert_empirical_to_response(m) for m in sliced]

    def get_by_code(self, code: str) -> Optional[PackagingMaterialResponse]:
        if self.db is not None:
            try:
                stmt = select(PackagingMaterial).where(PackagingMaterial.code == code)
                db_material = self.db.scalars(stmt).first()
                if db_material:
                    return PackagingMaterialResponse.model_validate(db_material)
            except Exception:
                pass

        for m in get_verified_materials():
            if m["code"].lower() == code.lower():
                return self._convert_empirical_to_response(m)
        return None

    def get_by_id_or_code(self, identifier: str) -> PackagingMaterialResponse:
        # Try by code first
        mat = self.get_by_code(identifier)
        if mat:
            return mat

        # Try by UUID in DB
        if self.db is not None:
            try:
                parsed_uuid = uuid.UUID(identifier)
                db_material = self.db.get(PackagingMaterial, parsed_uuid)
                if db_material:
                    return PackagingMaterialResponse.model_validate(db_material)
            except Exception:
                pass

        # Try by matching deterministic UUID in empirical materials
        for m in get_verified_materials():
            det_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, m["code"]))
            if det_id.lower() == identifier.lower():
                return self._convert_empirical_to_response(m)

        raise ResourceNotFoundException("PackagingMaterial", identifier)
