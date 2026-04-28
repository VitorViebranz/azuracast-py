import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user, require_super_admin
from src.modules.playlists.schemas import (
    PlaylistCreate,
    PlaylistItemAdd,
    PlaylistItemReorder,
    PlaylistResponse,
    PlaylistUpdate,
)
from src.modules.playlists.service import PlaylistService
from src.modules.stations.service import StationService
from src.modules.users.models import User

router = APIRouter(prefix="/stations/{station_id}/playlists", tags=["playlists"])


@router.get("", response_model=list[PlaylistResponse], summary="List playlists for a station")
async def list_playlists(
    station_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await StationService(db).get_station(station_id)
    return await PlaylistService(db).list_playlists(station_id, skip=skip, limit=limit)


@router.post("", response_model=PlaylistResponse, status_code=201, summary="Create a playlist")
async def create_playlist(
    station_id: uuid.UUID,
    data: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    await StationService(db).get_station(station_id)
    return await PlaylistService(db).create_playlist(station_id, data)


@router.get("/{playlist_id}", response_model=PlaylistResponse, summary="Get a playlist")
async def get_playlist(
    station_id: uuid.UUID,
    playlist_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await PlaylistService(db).get_playlist(station_id, playlist_id)


@router.put("/{playlist_id}", response_model=PlaylistResponse, summary="Update a playlist")
async def update_playlist(
    station_id: uuid.UUID,
    playlist_id: uuid.UUID,
    data: PlaylistUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await PlaylistService(db).update_playlist(station_id, playlist_id, data)


@router.delete("/{playlist_id}", status_code=204, summary="Delete a playlist")
async def delete_playlist(
    station_id: uuid.UUID,
    playlist_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    await PlaylistService(db).delete_playlist(station_id, playlist_id)


@router.post(
    "/{playlist_id}/items",
    response_model=PlaylistResponse,
    status_code=201,
    summary="Add a track to a playlist",
)
async def add_item(
    station_id: uuid.UUID,
    playlist_id: uuid.UUID,
    data: PlaylistItemAdd,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await PlaylistService(db).add_item(station_id, playlist_id, data)


@router.delete(
    "/{playlist_id}/items/{item_id}",
    response_model=PlaylistResponse,
    summary="Remove a track from a playlist",
)
async def remove_item(
    station_id: uuid.UUID,
    playlist_id: uuid.UUID,
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await PlaylistService(db).remove_item(station_id, playlist_id, item_id)


@router.put(
    "/{playlist_id}/items/reorder",
    response_model=PlaylistResponse,
    summary="Reorder playlist items",
)
async def reorder_items(
    station_id: uuid.UUID,
    playlist_id: uuid.UUID,
    data: PlaylistItemReorder,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    return await PlaylistService(db).reorder_items(station_id, playlist_id, data)
