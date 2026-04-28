import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.playlists.models import Playlist, PlaylistItem


class PlaylistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, playlist_id: uuid.UUID) -> Playlist | None:
        result = await self.db.execute(
            select(Playlist)
            .where(Playlist.id == playlist_id)
            .options(selectinload(Playlist.items).selectinload(PlaylistItem.media))
        )
        return result.scalar_one_or_none()

    async def list_by_station(self, station_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Playlist]:
        result = await self.db.execute(
            select(Playlist)
            .where(Playlist.station_id == station_id)
            .options(selectinload(Playlist.items).selectinload(PlaylistItem.media))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, playlist: Playlist) -> Playlist:
        self.db.add(playlist)
        await self.db.commit()
        await self.db.refresh(playlist)
        return await self.get_by_id(playlist.id)  # type: ignore[return-value]

    async def update(self, playlist: Playlist) -> Playlist:
        await self.db.commit()
        return await self.get_by_id(playlist.id)  # type: ignore[return-value]

    async def delete(self, playlist: Playlist) -> None:
        await self.db.delete(playlist)
        await self.db.commit()

    async def get_item_by_id(self, item_id: uuid.UUID) -> PlaylistItem | None:
        result = await self.db.execute(
            select(PlaylistItem)
            .where(PlaylistItem.id == item_id)
            .options(selectinload(PlaylistItem.media))
        )
        return result.scalar_one_or_none()

    async def get_item_by_playlist_and_media(
        self, playlist_id: uuid.UUID, media_id: uuid.UUID
    ) -> PlaylistItem | None:
        result = await self.db.execute(
            select(PlaylistItem).where(
                PlaylistItem.playlist_id == playlist_id,
                PlaylistItem.media_id == media_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_item(self, item: PlaylistItem) -> PlaylistItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_item(self, item: PlaylistItem) -> None:
        await self.db.delete(item)
        await self.db.commit()

    async def bulk_update_positions(self, items: list[PlaylistItem]) -> None:
        for item in items:
            self.db.add(item)
        await self.db.commit()
