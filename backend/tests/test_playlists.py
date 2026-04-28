import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.modules.media.models import MediaFile
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
        name=f"PL Station {uuid.uuid4().hex[:6]}",
        short_name=f"pl-st-{uuid.uuid4().hex[:6]}",
    )
    db_session.add(station)
    await db_session.commit()
    await db_session.refresh(station)
    return station


async def upload_media(
    client: AsyncClient, station_id: uuid.UUID, headers: dict, name: str = "track.mp3"
) -> str:
    content = b"ID3" + b"\x00" * 50
    files = {"file": (name, io.BytesIO(content), "audio/mpeg")}
    resp = await client.post(f"/api/v1/stations/{station_id}/media", headers=headers, files=files)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.anyio
async def test_create_and_list_playlists(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists",
        headers=headers,
        json={"name": "Top Hits", "weight": 5},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Top Hits"
    assert data["weight"] == 5
    assert data["items"] == []

    list_resp = await client.get(f"/api/v1/stations/{station.id}/playlists", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


@pytest.mark.anyio
async def test_add_and_remove_item(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)
    media_id = await upload_media(client, station.id, headers)

    # Create playlist
    pl_resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists",
        headers=headers,
        json={"name": "Chill Vibes"},
    )
    playlist_id = pl_resp.json()["id"]

    # Add item
    add_resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}/items",
        headers=headers,
        json={"media_id": media_id},
    )
    assert add_resp.status_code == 201
    assert len(add_resp.json()["items"]) == 1

    # Duplicate check
    dup_resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}/items",
        headers=headers,
        json={"media_id": media_id},
    )
    assert dup_resp.status_code == 400

    # Remove item
    item_id = add_resp.json()["items"][0]["id"]
    rem_resp = await client.delete(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}/items/{item_id}",
        headers=headers,
    )
    assert rem_resp.status_code == 200
    assert rem_resp.json()["items"] == []


@pytest.mark.anyio
async def test_reorder_items(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    media_a = await upload_media(client, station.id, headers, "a.mp3")
    media_b = await upload_media(client, station.id, headers, "b.mp3")
    media_c = await upload_media(client, station.id, headers, "c.mp3")

    pl_resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists",
        headers=headers,
        json={"name": "Reorder Test"},
    )
    playlist_id = pl_resp.json()["id"]

    for mid in (media_a, media_b, media_c):
        await client.post(
            f"/api/v1/stations/{station.id}/playlists/{playlist_id}/items",
            headers=headers,
            json={"media_id": mid},
        )

    pl_detail = await client.get(f"/api/v1/stations/{station.id}/playlists/{playlist_id}", headers=headers)
    items = pl_detail.json()["items"]
    assert len(items) == 3
    item_ids = [i["id"] for i in items]
    reversed_ids = list(reversed(item_ids))

    reorder_resp = await client.put(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}/items/reorder",
        headers=headers,
        json={"item_ids": reversed_ids},
    )
    assert reorder_resp.status_code == 200
    new_items = reorder_resp.json()["items"]
    assert [i["id"] for i in new_items] == reversed_ids


@pytest.mark.anyio
async def test_update_playlist(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    pl_resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists",
        headers=headers,
        json={"name": "Old Name", "weight": 1},
    )
    playlist_id = pl_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}",
        headers=headers,
        json={"name": "New Name", "weight": 8},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Name"
    assert update_resp.json()["weight"] == 8


@pytest.mark.anyio
async def test_delete_playlist(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr("src.modules.media.service.settings.MEDIA_ROOT", str(tmp_path))
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    pl_resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists",
        headers=headers,
        json={"name": "Disposable"},
    )
    playlist_id = pl_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}", headers=headers
    )
    assert del_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/stations/{station.id}/playlists/{playlist_id}", headers=headers
    )
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_invalid_weight(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"******"}
    station = await create_station(db_session)

    resp = await client.post(
        f"/api/v1/stations/{station.id}/playlists",
        headers=headers,
        json={"name": "Bad Weight", "weight": 15},
    )
    assert resp.status_code == 422
