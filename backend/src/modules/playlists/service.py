import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.playlists.models import Playlist, PlaylistItem
from src.modules.playlists.repository import PlaylistRepository
from src.modules.playlists.schemas import PlaylistCreate, PlaylistItemAdd, PlaylistItemReorder, PlaylistUpdate


class PlaylistService:
    def __init__(self, db: AsyncSession):
        self.repo = PlaylistRepository(db)

    async def create_playlist(self, station_id: uuid.UUID, data: PlaylistCreate) -> Playlist:
        playlist = Playlist(station_id=station_id, **data.model_dump())
        return await self.repo.create(playlist)

    async def get_playlist(self, station_id: uuid.UUID, playlist_id: uuid.UUID) -> Playlist:
        playlist = await self.repo.get_by_id(playlist_id)
        if not playlist or playlist.station_id != station_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
        return playlist

    async def list_playlists(self, station_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Playlist]:
        return await self.repo.list_by_station(station_id, skip=skip, limit=limit)

    async def update_playlist(
        self, station_id: uuid.UUID, playlist_id: uuid.UUID, data: PlaylistUpdate
    ) -> Playlist:
        playlist = await self.get_playlist(station_id, playlist_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(playlist, field, value)
        return await self.repo.update(playlist)

    async def delete_playlist(self, station_id: uuid.UUID, playlist_id: uuid.UUID) -> None:
        playlist = await self.get_playlist(station_id, playlist_id)
        await self.repo.delete(playlist)

    async def add_item(
        self, station_id: uuid.UUID, playlist_id: uuid.UUID, data: PlaylistItemAdd
    ) -> Playlist:
        playlist = await self.get_playlist(station_id, playlist_id)
        existing = await self.repo.get_item_by_playlist_and_media(playlist_id, data.media_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Track already in playlist")
        position = len(playlist.items)
        item = PlaylistItem(playlist_id=playlist_id, media_id=data.media_id, position=position)
        await self.repo.add_item(item)
        return await self.repo.get_by_id(playlist_id)  # type: ignore[return-value]

    async def remove_item(
        self, station_id: uuid.UUID, playlist_id: uuid.UUID, item_id: uuid.UUID
    ) -> Playlist:
        playlist = await self.get_playlist(station_id, playlist_id)
        item = await self.repo.get_item_by_id(item_id)
        if not item or item.playlist_id != playlist_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        await self.repo.delete_item(item)
        # Re-sequence positions
        updated_playlist = await self.repo.get_by_id(playlist_id)
        if updated_playlist:
            for idx, remaining_item in enumerate(updated_playlist.items):
                remaining_item.position = idx
            await self.repo.bulk_update_positions(list(updated_playlist.items))
        return await self.repo.get_by_id(playlist_id)  # type: ignore[return-value]

    async def reorder_items(
        self, station_id: uuid.UUID, playlist_id: uuid.UUID, data: PlaylistItemReorder
    ) -> Playlist:
        playlist = await self.get_playlist(station_id, playlist_id)
        item_map = {item.id: item for item in playlist.items}
        if set(data.item_ids) != set(item_map.keys()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="item_ids must contain exactly all item IDs in the playlist",
            )
        for position, item_id in enumerate(data.item_ids):
            item_map[item_id].position = position
        await self.repo.bulk_update_positions(list(item_map.values()))
        return await self.repo.get_by_id(playlist_id)  # type: ignore[return-value]
