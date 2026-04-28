import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.stations.service import StationService
from src.modules.users.models import User
from src.services.liquidsoap import liquidsoap_service
from src.services.sse import sse_manager

router = APIRouter(tags=["now-playing"])


# ---------------------------------------------------------------------------
# Now-Playing SSE stream
# ---------------------------------------------------------------------------


@router.get(
    "/stations/{station_id}/now-playing/stream",
    summary="Subscribe to now-playing events via Server-Sent Events",
    response_class=StreamingResponse,
)
async def now_playing_stream(
    station_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await StationService(db).get_station(station_id)
    queue = await sse_manager.subscribe(station_id)

    async def event_generator():
        async for chunk in sse_manager.stream(station_id, queue):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Liquidsoap webhook — called by Liquidsoap on every track change
# ---------------------------------------------------------------------------


class NowPlayingWebhook(BaseModel):
    title: str | None = None
    artist: str | None = None
    album: str | None = None


@router.post(
    "/stations/{station_id}/now-playing",
    status_code=204,
    summary="Liquidsoap webhook — report currently playing track",
)
async def now_playing_webhook(
    station_id: uuid.UUID,
    data: NowPlayingWebhook,
    db: AsyncSession = Depends(get_db),
):
    # Verify station exists (raises 404 if not)
    await StationService(db).get_station(station_id)
    await sse_manager.publish(
        station_id,
        "now_playing",
        {
            "station_id": str(station_id),
            "title": data.title,
            "artist": data.artist,
            "album": data.album,
        },
    )


# ---------------------------------------------------------------------------
# Liquidsoap config generator
# ---------------------------------------------------------------------------


@router.post(
    "/stations/{station_id}/liquidsoap/generate",
    status_code=200,
    summary="(Re)generate the Liquidsoap .liq config for a station",
)
async def generate_liquidsoap_config(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    station = await StationService(db).get_station(station_id)
    # Load playlists and active mounts
    from src.modules.playlists.repository import PlaylistRepository

    playlists = await PlaylistRepository(db).list_by_station(station_id)
    active_mounts = [m for m in station.mount_points if m.is_public]
    config_path = await liquidsoap_service.write_config(station, playlists, active_mounts)
    reloaded = await liquidsoap_service.reload()
    return {
        "config_path": str(config_path),
        "liquidsoap_reloaded": reloaded,
    }
