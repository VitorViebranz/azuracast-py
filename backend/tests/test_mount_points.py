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


@pytest.mark.anyio
async def test_list_mounts_unauthenticated(client: AsyncClient, db_session: AsyncSession):
    station = await create_station(db_session)
    response = await client.get(f"/api/v1/stations/{station.id}/mounts")
    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_create_and_list_mount_points(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    response = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "Main Mount", "mount_path": "/stream.mp3"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Main Mount"
    assert data["mount_path"] == "/stream.mp3"
    assert data["station_id"] == str(station.id)

    list_response = await client.get(f"/api/v1/stations/{station.id}/mounts", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1


@pytest.mark.anyio
async def test_create_mount_duplicate_path(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "Mount A", "mount_path": "/radio.mp3"},
        headers=headers,
    )
    response = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "Mount B", "mount_path": "/radio.mp3"},
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_mount_point(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    create_resp = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "OGG Mount", "mount_path": "/stream.ogg", "format": "ogg"},
        headers=headers,
    )
    mount_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/stations/{station.id}/mounts/{mount_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == mount_id
    assert response.json()["format"] == "ogg"


@pytest.mark.anyio
async def test_update_mount_point(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    create_resp = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "Mount", "mount_path": "/live.mp3"},
        headers=headers,
    )
    mount_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/stations/{station.id}/mounts/{mount_id}",
        json={"name": "Updated Mount", "is_default": True},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Mount"
    assert response.json()["is_default"] is True


@pytest.mark.anyio
async def test_delete_mount_point(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    create_resp = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "To Delete", "mount_path": "/delete.mp3"},
        headers=headers,
    )
    mount_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/stations/{station.id}/mounts/{mount_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/stations/{station.id}/mounts/{mount_id}", headers=headers)
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_mount_point_invalid_path(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    response = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "Bad Path", "mount_path": "no-leading-slash"},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_mount_point_invalid_format(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    station = await create_station(db_session)

    response = await client.post(
        f"/api/v1/stations/{station.id}/mounts",
        json={"name": "Bad Format", "mount_path": "/test.flac", "format": "flac"},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_station_response_includes_mount_points(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    station_resp = await client.post(
        "/api/v1/stations",
        json={"name": "Mounts Station", "short_name": f"mounts-st-{uuid.uuid4().hex[:6]}"},
        headers=headers,
    )
    station_id = station_resp.json()["id"]

    await client.post(
        f"/api/v1/stations/{station_id}/mounts",
        json={"name": "First Mount", "mount_path": "/first.mp3"},
        headers=headers,
    )

    response = await client.get(f"/api/v1/stations/{station_id}", headers=headers)
    assert response.status_code == 200
    assert "mount_points" in response.json()
    assert len(response.json()["mount_points"]) == 1
