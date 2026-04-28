import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.mount_points.models import MountPoint
from src.modules.mount_points.repository import MountPointRepository
from src.modules.mount_points.schemas import MountPointCreate, MountPointUpdate


class MountPointService:
    def __init__(self, db: AsyncSession):
        self.repo = MountPointRepository(db)

    async def create_mount_point(self, station_id: uuid.UUID, data: MountPointCreate) -> MountPoint:
        if await self.repo.get_by_station_and_path(station_id, data.mount_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A mount point with this path already exists for this station",
            )
        mount = MountPoint(station_id=station_id, **data.model_dump())
        return await self.repo.create(mount)

    async def get_mount_point(self, station_id: uuid.UUID, mount_id: uuid.UUID) -> MountPoint:
        mount = await self.repo.get_by_id(mount_id)
        if not mount or mount.station_id != station_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mount point not found")
        return mount

    async def list_mount_points(
        self, station_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[MountPoint]:
        return await self.repo.list_by_station(station_id, skip=skip, limit=limit)

    async def update_mount_point(
        self, station_id: uuid.UUID, mount_id: uuid.UUID, data: MountPointUpdate
    ) -> MountPoint:
        mount = await self.get_mount_point(station_id, mount_id)
        updates = data.model_dump(exclude_unset=True)
        if "mount_path" in updates and updates["mount_path"] != mount.mount_path:
            if await self.repo.get_by_station_and_path(station_id, updates["mount_path"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A mount point with this path already exists for this station",
                )
        for field, value in updates.items():
            setattr(mount, field, value)
        return await self.repo.update(mount)

    async def delete_mount_point(self, station_id: uuid.UUID, mount_id: uuid.UUID) -> None:
        mount = await self.get_mount_point(station_id, mount_id)
        await self.repo.delete(mount)
