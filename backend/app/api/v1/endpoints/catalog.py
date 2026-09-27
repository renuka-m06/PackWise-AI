from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db_optional
from app.schemas.commodity import CommodityResponse
from app.schemas.material import PackagingMaterialResponse
from app.services.commodity_service import CommodityService
from app.services.material_service import MaterialService

router = APIRouter()


@router.get(
    "/commodities",
    response_model=List[CommodityResponse],
    status_code=status.HTTP_200_OK,
    summary="List Supported Commodities",
    description="Returns registered commodity profiles and biological parameters."
)
def list_commodities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Optional[Session] = Depends(get_db_optional)
):
    service = CommodityService(db=db)
    return service.get_all(skip=skip, limit=limit)


@router.get(
    "/commodities/{identifier}",
    response_model=CommodityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Commodity Profile by Name or UUID",
    description="Returns detailed physiological respiration and storage constraints for a verified commodity."
)
def get_commodity_by_identifier(
    identifier: str,
    db: Optional[Session] = Depends(get_db_optional)
):
    service = CommodityService(db=db)
    return service.get_by_id_or_name(identifier)


@router.get(
    "/materials",
    response_model=List[PackagingMaterialResponse],
    status_code=status.HTTP_200_OK,
    summary="List Packaging Materials Catalog",
    description="Returns registered packaging materials with barrier properties (OTR/WVTR)."
)
def list_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Optional[Session] = Depends(get_db_optional)
):
    service = MaterialService(db=db)
    return service.get_all(skip=skip, limit=limit)


@router.get(
    "/materials/{identifier}",
    response_model=PackagingMaterialResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Packaging Material by Code or UUID",
    description="Returns full technical data sheet properties, ASTM barrier ratings, and food contact safety status."
)
def get_material_by_identifier(
    identifier: str,
    db: Optional[Session] = Depends(get_db_optional)
):
    service = MaterialService(db=db)
    return service.get_by_id_or_code(identifier)
