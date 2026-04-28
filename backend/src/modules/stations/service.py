import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.stations.models import Station
from src.modules.stations.repository import StationRepository
from src.modules.stations.schemas import StationCreate, StationUpdate


class StationService:
    def __init__(self, db: AsyncSession):
        self.repo = StationRepository(db)

    async def create_station(self, data: StationCreate) -> Station:
        if await self.repo.get_by_short_name(data.short_name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Short name already in use")
        station = Station(**data.model_dump())
        return await self.repo.create(station)

    async def get_station(self, station_id: uuid.UUID) -> Station:
        station = await self.repo.get_by_id(station_id)
        if not station:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
        return station

    async def list_stations(self, skip: int = 0, limit: int = 100) -> list[Station]:
        return await self.repo.list_all(skip=skip, limit=limit)

    async def update_station(self, station_id: uuid.UUID, data: StationUpdate) -> Station:
        station = await self.get_station(station_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(station, field, value)
        return await self.repo.update(station)

    async def delete_station(self, station_id: uuid.UUID) -> None:
        station = await self.get_station(station_id)
        await self.repo.delete(station)
