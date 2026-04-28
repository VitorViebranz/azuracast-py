import asyncio
import logging
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.modules.media.models import MediaFile
from src.modules.media.repository import MediaRepository
from src.modules.media.schemas import ALLOWED_MIME_TYPES, MediaFileUpdate

logger = logging.getLogger(__name__)


def _extract_metadata_sync(file_path: Path) -> dict:
    """Run mutagen synchronously — called via asyncio.to_thread."""
    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(str(file_path), easy=True)
        if audio is None:
            return {}
        info = audio.info
        result: dict = {
            "duration": getattr(info, "length", None),
            "bitrate": getattr(info, "bitrate", None),
            "sample_rate": getattr(info, "sample_rate", None),
        }
        tags = audio.tags or {}
        for key in ("title", "artist", "album"):
            values = tags.get(key)
            if values:
                result[key] = str(values[0]) if isinstance(values, list) else str(values)
        return result
    except Exception:
        logger.warning("Failed to extract metadata from %s", file_path)
        return {}


class MediaService:
    def __init__(self, db: AsyncSession):
        self.repo = MediaRepository(db)

    def _station_media_dir(self, station_short_name: str) -> Path:
        return Path(settings.MEDIA_ROOT) / station_short_name

    def _storage_path(self, station_short_name: str, storage_filename: str) -> Path:
        return self._station_media_dir(station_short_name) / storage_filename

    async def upload_file(
        self,
        station_id: uuid.UUID,
        station_short_name: str,
        file: UploadFile,
    ) -> MediaFile:
        mime_type = file.content_type or "application/octet-stream"
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {mime_type}. Allowed: {sorted(ALLOWED_MIME_TYPES)}",
            )
        original_filename = file.filename or "upload"
        suffix = Path(original_filename).suffix.lower()
        storage_filename = f"{uuid.uuid4().hex}{suffix}"
        media_dir = self._station_media_dir(station_short_name)
        media_dir.mkdir(parents=True, exist_ok=True)
        storage_path = media_dir / storage_filename
        content = await file.read()
        async with aiofiles.open(storage_path, "wb") as f:
            await f.write(content)
        file_size = len(content)
        media = MediaFile(
            station_id=station_id,
            original_filename=original_filename,
            storage_filename=storage_filename,
            mime_type=mime_type,
            file_size=file_size,
            metadata_synced=False,
        )
        media = await self.repo.create(media)
        asyncio.create_task(self._sync_metadata(media.id, storage_path))
        return media

    async def _sync_metadata(self, media_id: uuid.UUID, file_path: Path) -> None:
        meta = await asyncio.to_thread(_extract_metadata_sync, file_path)
        if not meta:
            return
        media = await self.repo.get_by_id(media_id)
        if not media:
            return
        for field in ("title", "artist", "album", "duration", "bitrate", "sample_rate"):
            value = meta.get(field)
            if value is not None:
                setattr(media, field, value)
        media.metadata_synced = True
        await self.repo.update(media)

    async def get_media(self, station_id: uuid.UUID, media_id: uuid.UUID) -> MediaFile:
        media = await self.repo.get_by_id(media_id)
        if not media or media.station_id != station_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
        return media

    async def list_media(
        self, station_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[MediaFile]:
        return await self.repo.list_by_station(station_id, skip=skip, limit=limit)

    async def update_media(
        self, station_id: uuid.UUID, media_id: uuid.UUID, data: MediaFileUpdate
    ) -> MediaFile:
        media = await self.get_media(station_id, media_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(media, field, value)
        return await self.repo.update(media)

    async def delete_media(
        self, station_id: uuid.UUID, media_id: uuid.UUID, station_short_name: str
    ) -> None:
        media = await self.get_media(station_id, media_id)
        storage_path = self._storage_path(station_short_name, media.storage_filename)
        await self.repo.delete(media)
        try:
            storage_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not delete file: %s", storage_path)
