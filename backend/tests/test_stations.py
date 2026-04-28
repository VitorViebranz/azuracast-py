import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.modules.users.models import User


async def create_superadmin(db_session: AsyncSession) -> str:
    import uuid

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


@pytest.mark.anyio
async def test_list_stations_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/stations")
    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_create_and_list_stations(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/stations",
        json={"name": "Test Station", "short_name": "test-station"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Station"

    list_response = await client.get("/api/v1/stations", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1


@pytest.mark.anyio
async def test_get_station(client: AsyncClient, db_session: AsyncSession):
    token = await create_superadmin(db_session)
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(
        "/api/v1/stations",
        json={"name": "Get Station", "short_name": f"get-station-{__import__('uuid').uuid4().hex[:8]}"},
        headers=headers,
    )
    station_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/stations/{station_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == station_id
