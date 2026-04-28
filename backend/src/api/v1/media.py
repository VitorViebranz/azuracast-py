import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user, require_super_admin
from src.modules.media.schemas import MediaFileResponse, MediaFileUpdate
from src.modules.media.service import MediaService
from src.modules.stations.service import StationService
from src.modules.users.models import User

router = APIRouter(prefix="/stations/{station_id}/media", tags=["media"])


@router.get("", response_model=list[MediaFileResponse], summary="List media files for a station")
async def list_media(
    station_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    station = await StationService(db).get_station(station_id)
    service = MediaService(db)
    return await service.list_media(station.id, skip=skip, limit=limit)


@router.post(
    "",
    response_model=MediaFileResponse,
    status_code=201,
    summary="Upload a media file to a station",
)
async def upload_media(
    station_id: uuid.UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks,  # noqa: ARG001 – kept for future background job upgrade
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    station = await StationService(db).get_station(station_id)
    service = MediaService(db)
    return await service.upload_file(station.id, station.short_name, file)


@router.get("/{media_id}", response_model=MediaFileResponse, summary="Get media file details")
async def get_media(
    station_id: uuid.UUID,
    media_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = MediaService(db)
    return await service.get_media(station_id, media_id)


@router.patch("/{media_id}", response_model=MediaFileResponse, summary="Update media file metadata")
async def update_media(
    station_id: uuid.UUID,
    media_id: uuid.UUID,
    data: MediaFileUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    service = MediaService(db)
    return await service.update_media(station_id, media_id, data)


@router.delete("/{media_id}", status_code=204, summary="Delete a media file")
async def delete_media(
    station_id: uuid.UUID,
    media_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    station = await StationService(db).get_station(station_id)
    service = MediaService(db)
    await service.delete_media(station_id, media_id, station.short_name)
