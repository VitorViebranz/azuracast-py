import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.modules.stations.models import Station
from src.modules.users.models import User


async def create_superadmin(db_session: AsyncSession) -> str:
    user = User(
        id=uuid.uuid4(),
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        username=f"admin_{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("adminpass"),
        is_super_admin=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    from src.core.security import create_access_token

    return create_access_token(str(user.id))


async def create_station(db_session: AsyncSession) -> Station:
    station = Station(
        id=uuid.uuid4(),
        name=f"Station {uuid.uuid4().hex[:6]}",
        short_name=f"st-{uuid.uuid4().hex[:8]}",
    )
    db_session.add(station)
    await db_session.commit()
    await db_session.refresh(station)
    return station


def make_audio_upload(filename: str = "track.mp3") -> tuple:
    """Return (files, content_type) for a fake audio multipart upload."""
    content = b"ID3" + b"\x00" * 100  # Fake MP3 header bytes
    return (
        {"file": (filename, io.BytesIO(content), "audio/mpeg")},
    )


@pytest.mark.anyio
async def test_list_media_unauthenticated(client: AsyncClient, db_session: AsyncSession):
    station = await create_station(db_session)
    response = await client.get(f"/api/v1/stations/{station.id}/media")
    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_upload_and_list_media(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    content = b"ID3" + b"\x00" * 100
    files = {"file": ("song.mp3", io.BytesIO(content), "audio/mpeg")}
    response = await client.post(
        f"/api/v1/stations/{station.id}/media",
        headers=headers,
        files=files,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "song.mp3"
    assert data["mime_type"] == "audio/mpeg"
    assert data["file_size"] == len(content)
    assert data["station_id"] == str(station.id)

    list_resp = await client.get(f"/api/v1/stations/{station.id}/media", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


@pytest.mark.anyio
async def test_upload_unsupported_mime(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    files = {"file": ("image.jpg", io.BytesIO(b"\xff\xd8\xff"), "image/jpeg")}
    response = await client.post(
        f"/api/v1/stations/{station.id}/media",
        headers=headers,
        files=files,
    )
    assert response.status_code == 415


@pytest.mark.anyio
async def test_get_media(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    files = {"file": ("track.mp3", io.BytesIO(b"ID3" + b"\x00" * 50), "audio/mpeg")}
    upload = await client.post(f"/api/v1/stations/{station.id}/media", headers=headers, files=files)
    media_id = upload.json()["id"]

    response = await client.get(f"/api/v1/stations/{station.id}/media/{media_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == media_id


@pytest.mark.anyio
async def test_update_media_metadata(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    files = {"file": ("track.mp3", io.BytesIO(b"ID3" + b"\x00" * 50), "audio/mpeg")}
    upload = await client.post(f"/api/v1/stations/{station.id}/media", headers=headers, files=files)
    media_id = upload.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/stations/{station.id}/media/{media_id}",
        headers=headers,
        json={"title": "My Song", "artist": "DJ Test"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "My Song"
    assert patch_resp.json()["artist"] == "DJ Test"


@pytest.mark.anyio
async def test_delete_media(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    files = {"file": ("delete_me.mp3", io.BytesIO(b"ID3" + b"\x00" * 50), "audio/mpeg")}
    upload = await client.post(f"/api/v1/stations/{station.id}/media", headers=headers, files=files)
    media_id = upload.json()["id"]

    del_resp = await client.delete(f"/api/v1/stations/{station.id}/media/{media_id}", headers=headers)
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/stations/{station.id}/media/{media_id}", headers=headers)
    assert get_resp.status_code == 404
