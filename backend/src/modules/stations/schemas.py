import uuid
from datetime import datetime

from pydantic import BaseModel


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

    model_config = {"from_attributes": True}
