from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.material import PackagingMaterial
from app.schemas.material import PackagingMaterialCreate
from app.core.exceptions import ResourceNotFoundException


class MaterialService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PackagingMaterial]:
        stmt = select(PackagingMaterial).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_code(self, code: str) -> Optional[PackagingMaterial]:
        stmt = select(PackagingMaterial).where(PackagingMaterial.code == code)
        return self.db.scalars(stmt).first()

    def get_by_id(self, material_id) -> PackagingMaterial:
        material = self.db.get(PackagingMaterial, material_id)
        if not material:
            raise ResourceNotFoundException("PackagingMaterial", str(material_id))
        return material

    def create(self, payload: PackagingMaterialCreate) -> PackagingMaterial:
        material = PackagingMaterial(**payload.model_dump())
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material
