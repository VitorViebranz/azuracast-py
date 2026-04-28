import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

ALLOWED_MIME_TYPES = {"audio/mpeg", "audio/ogg", "audio/aac", "audio/opus", "audio/flac", "audio/wav"}


class MediaFileResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size: int
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    duration: float | None = None
    bitrate: int | None = None
    sample_rate: int | None = None
    metadata_synced: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MediaFileUpdate(BaseModel):
    title: str | None = None
    artist: str | None = None
    album: str | None = None

    @field_validator("title", "artist", "album", mode="before")
    @classmethod
    def strip_empty(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            return None
        return v
