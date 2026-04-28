import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user, require_super_admin
from src.modules.mount_points.schemas import MountPointCreate, MountPointResponse, MountPointUpdate
from src.modules.mount_points.service import MountPointService
from src.modules.stations.service import StationService
from src.modules.users.models import User

router = APIRouter(prefix="/stations/{station_id}/mounts", tags=["mount-points"])


@router.get("", response_model=list[MountPointResponse], summary="List mount points for a station")
async def list_mount_points(
    station_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await StationService(db).get_station(station_id)
    service = MountPointService(db)
    return await service.list_mount_points(station_id, skip=skip, limit=limit)


@router.post("", response_model=MountPointResponse, status_code=201, summary="Create mount point")
async def create_mount_point(
    station_id: uuid.UUID,
    data: MountPointCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    await StationService(db).get_station(station_id)
    service = MountPointService(db)
    return await service.create_mount_point(station_id, data)


@router.get("/{mount_id}", response_model=MountPointResponse, summary="Get mount point")
async def get_mount_point(
    station_id: uuid.UUID,
    mount_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = MountPointService(db)
    return await service.get_mount_point(station_id, mount_id)


@router.put("/{mount_id}", response_model=MountPointResponse, summary="Update mount point")
async def update_mount_point(
    station_id: uuid.UUID,
    mount_id: uuid.UUID,
    data: MountPointUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    service = MountPointService(db)
    return await service.update_mount_point(station_id, mount_id, data)


@router.delete("/{mount_id}", status_code=204, summary="Delete mount point")
async def delete_mount_point(
    station_id: uuid.UUID,
    mount_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    service = MountPointService(db)
    await service.delete_mount_point(station_id, mount_id)
