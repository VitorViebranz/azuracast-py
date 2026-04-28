import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.stations.models import Station


class StationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, station_id: uuid.UUID) -> Station | None:
        result = await self.db.execute(select(Station).where(Station.id == station_id))
        return result.scalar_one_or_none()

    async def get_by_short_name(self, short_name: str) -> Station | None:
        result = await self.db.execute(select(Station).where(Station.short_name == short_name))
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Station]:
        result = await self.db.execute(select(Station).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, station: Station) -> Station:
        self.db.add(station)
        await self.db.commit()
        await self.db.refresh(station)
        return station

    async def update(self, station: Station) -> Station:
        await self.db.commit()
        await self.db.refresh(station)
        return station

    async def delete(self, station: Station) -> None:
        await self.db.delete(station)
        await self.db.commit()
