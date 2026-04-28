import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class PlaylistItemResponse(BaseModel):
    id: uuid.UUID
    playlist_id: uuid.UUID
    media_id: uuid.UUID
    position: int
    created_at: datetime
    # Flattened media info for convenience
    media_original_filename: str | None = None
    media_title: str | None = None
    media_artist: str | None = None
    media_duration: float | None = None

    model_config = {"from_attributes": True}


class PlaylistBase(BaseModel):
    name: str
    description: str | None = None
    weight: int = 3

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("weight must be between 1 and 10")
        return v


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    weight: int | None = None

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 10):
            raise ValueError("weight must be between 1 and 10")
        return v


class PlaylistResponse(PlaylistBase):
    id: uuid.UUID
    station_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    items: list[PlaylistItemResponse] = []

    model_config = {"from_attributes": True}


class PlaylistItemAdd(BaseModel):
    media_id: uuid.UUID


class PlaylistItemReorder(BaseModel):
    item_ids: list[uuid.UUID]

    @field_validator("item_ids")
    @classmethod
    def no_duplicates(cls, v: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(v) != len(set(v)):
            raise ValueError("item_ids must not contain duplicates")
        return v
