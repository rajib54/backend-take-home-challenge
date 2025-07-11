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

async def cleanup_slug(async_test_db, slug: str):
    """Remove URL and associated visits from DB after test."""
    from sqlalchemy import delete
    from app.models.visit import Visit
    from app.models.urls import URL

    await async_test_db.execute(delete(Visit).where(Visit.url_id == URL.id).where(URL.slug == slug))
    await async_test_db.execute(delete(URL).where(URL.slug == slug))
    await async_test_db.commit()


@pytest.mark.asyncio
async def test_shorten_invalid_body_returns_400(async_client):
    res = await async_client.post("/shorten", json={"invalid_key": "value"})
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_shorten_same_url_returns_same_slug(async_client, async_test_db):
    long_url = "https://repeat.com"
    
    # First shorten
    res1 = await async_client.post("/shorten", json={"long_url": long_url})
    slug1 = res1.json()["slug"]

    # Second shorten
    res2 = await async_client.post("/shorten", json={"long_url": long_url})
    slug2 = res2.json()["slug"]

    assert slug1 == slug2

    await cleanup_slug(async_test_db, slug1)
    await cleanup_slug(async_test_db, slug2)

