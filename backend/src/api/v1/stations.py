import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user, require_super_admin
from src.modules.stations.schemas import StationCreate, StationResponse, StationUpdate
from src.modules.stations.service import StationService
from src.modules.users.models import User

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("", response_model=list[StationResponse], summary="List stations")
async def list_stations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = StationService(db)
    return await service.list_stations(skip=skip, limit=limit)


@router.post("", response_model=StationResponse, status_code=201, summary="Create station")
async def create_station(
    data: StationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    service = StationService(db)
    return await service.create_station(data)


@router.get("/{station_id}", response_model=StationResponse, summary="Get station")
async def get_station(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = StationService(db)
    return await service.get_station(station_id)


@router.put("/{station_id}", response_model=StationResponse, summary="Update station")
async def update_station(
    station_id: uuid.UUID,
    data: StationUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    service = StationService(db)
    return await service.update_station(station_id, data)


@router.delete("/{station_id}", status_code=204, summary="Delete station")
async def delete_station(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    service = StationService(db)
    await service.delete_station(station_id)
