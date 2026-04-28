import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class MountPointBase(BaseModel):
    name: str
    display_name: str | None = None
    mount_path: str
    is_default: bool = False
    is_public: bool = True
    max_listeners: int = 100
    bitrate: int = 128
    format: str = "mp3"

    @field_validator("mount_path")
    @classmethod
    def validate_mount_path(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("mount_path must start with /")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed = {"mp3", "ogg", "aac", "opus"}
        if v not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v


class MountPointCreate(MountPointBase):
    pass


class MountPointUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    mount_path: str | None = None
    is_default: bool | None = None
    is_public: bool | None = None
    max_listeners: int | None = None
    bitrate: int | None = None
    format: str | None = None

    @field_validator("mount_path")
    @classmethod
    def validate_mount_path(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("/"):
            raise ValueError("mount_path must start with /")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"mp3", "ogg", "aac", "opus"}
            if v not in allowed:
                raise ValueError(f"format must be one of {allowed}")
        return v


class MountPointResponse(MountPointBase):
    id: uuid.UUID
    station_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
