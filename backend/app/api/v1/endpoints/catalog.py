from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.commodity import CommodityResponse
from app.schemas.material import PackagingMaterialResponse
from app.services.commodity_service import CommodityService
from app.services.material_service import MaterialService

router = APIRouter()


@router.get(
    "/commodities",
    response_model=List[CommodityResponse],
    summary="List Supported Commodities",
    description="Returns registered commodity profiles and biological parameters."
)
def list_commodities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = CommodityService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get(
    "/materials",
    response_model=List[PackagingMaterialResponse],
    summary="List Packaging Materials Catalog",
    description="Returns registered packaging materials with barrier properties (OTR/WVTR)."
)
def list_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = MaterialService(db)
    return service.get_all(skip=skip, limit=limit)
