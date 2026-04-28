import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.mount_points.models import MountPoint


class MountPointRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, mount_id: uuid.UUID) -> MountPoint | None:
        result = await self.db.execute(select(MountPoint).where(MountPoint.id == mount_id))
        return result.scalar_one_or_none()

    async def get_by_station_and_path(self, station_id: uuid.UUID, mount_path: str) -> MountPoint | None:
        result = await self.db.execute(
            select(MountPoint).where(
                MountPoint.station_id == station_id,
                MountPoint.mount_path == mount_path,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_station(self, station_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[MountPoint]:
        result = await self.db.execute(
            select(MountPoint).where(MountPoint.station_id == station_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, mount: MountPoint) -> MountPoint:
        self.db.add(mount)
        await self.db.commit()
        await self.db.refresh(mount)
        return mount

    async def update(self, mount: MountPoint) -> MountPoint:
        await self.db.commit()
        await self.db.refresh(mount)
        return mount

    async def delete(self, mount: MountPoint) -> None:
        await self.db.delete(mount)
        await self.db.commit()
