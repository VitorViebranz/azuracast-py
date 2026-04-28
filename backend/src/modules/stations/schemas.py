import uuid
from datetime import datetime

from pydantic import BaseModel


class MountPointSummary(BaseModel):
    id: uuid.UUID
    name: str
    mount_path: str
    is_default: bool
    is_public: bool
    bitrate: int
    format: str

    model_config = {"from_attributes": True}


class StationBase(BaseModel):
    name: str
    short_name: str
    description: str | None = None
    timezone: str = "UTC"
    is_enabled: bool = True
    max_bitrate: int = 128
    max_mounts: int = 5


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    description: str | None = None
    timezone: str | None = None
    is_enabled: bool | None = None
    max_bitrate: int | None = None
    max_mounts: int | None = None


class StationResponse(StationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    mount_points: list[MountPointSummary] = []

    model_config = {"from_attributes": True}
