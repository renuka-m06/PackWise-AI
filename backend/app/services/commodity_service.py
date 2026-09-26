from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.commodity import Commodity
from app.schemas.commodity import CommodityCreate
from app.core.exceptions import ResourceNotFoundException


class CommodityService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Commodity]:
        stmt = select(Commodity).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_name(self, name: str) -> Optional[Commodity]:
        stmt = select(Commodity).where(Commodity.name.ilike(name))
        return self.db.scalars(stmt).first()

    def get_by_id(self, commodity_id) -> Commodity:
        commodity = self.db.get(Commodity, commodity_id)
        if not commodity:
            raise ResourceNotFoundException("Commodity", str(commodity_id))
        return commodity

    def create(self, payload: CommodityCreate) -> Commodity:
        commodity = Commodity(**payload.model_dump())
        self.db.add(commodity)
        self.db.commit()
        self.db.refresh(commodity)
        return commodity
