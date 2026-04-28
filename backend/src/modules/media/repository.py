import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.media.models import MediaFile


class MediaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, media_id: uuid.UUID) -> MediaFile | None:
        result = await self.db.execute(select(MediaFile).where(MediaFile.id == media_id))
        return result.scalar_one_or_none()

    async def list_by_station(self, station_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[MediaFile]:
        result = await self.db.execute(
            select(MediaFile)
            .where(MediaFile.station_id == station_id)
            .order_by(MediaFile.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_station(self, station_id: uuid.UUID) -> int:
        from sqlalchemy import func

        result = await self.db.execute(
            select(func.count()).select_from(MediaFile).where(MediaFile.station_id == station_id)
        )
        return result.scalar_one()

    async def create(self, media: MediaFile) -> MediaFile:
        self.db.add(media)
        await self.db.commit()
        await self.db.refresh(media)
        return media

    async def update(self, media: MediaFile) -> MediaFile:
        await self.db.commit()
        await self.db.refresh(media)
        return media

    async def delete(self, media: MediaFile) -> None:
        await self.db.delete(media)
        await self.db.commit()
