import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db, async_session
from app.utils.cache import delete_cache


@pytest.fixture()
async def async_test_db():
    async with async_session() as session:
        yield session


@pytest.fixture()
async def async_client(async_test_db):
    async def override_get_db():
        yield async_test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_shorten_invalid_body_returns_400(async_client):
    res = await async_client.post("/shorten", json={"invalid_key": "value"})
    assert res.status_code == 422  # FastAPI validation error
