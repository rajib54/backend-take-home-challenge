import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.urls import URL
from app.models.sequence import SlugSequence
from app.services import url as service
from app.services.const import SLUG_CACHE_KEY_TEMPLATE, TOP_N_SLUG_CACHE_KEY

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
@patch("app.services.url.handler.get_url_by_long_url")
@patch("app.services.url.generate_slug_with_sequence")
@patch("app.services.url.handler.create_url")
async def test_create_or_get_short_url_new(
    mock_create_url, mock_generate_slug, mock_get_by_long, mock_db
):
    mock_get_by_long.return_value = None
    mock_generate_slug.return_value = "abc123"
    fake_url = URL(id=1, slug="abc123", long_url="https://x.com")
    mock_create_url.return_value = fake_url

    result = await service.create_or_get_short_url(mock_db, "https://x.com")
    assert result.slug == "abc123"
    mock_create_url.assert_awaited_once_with(mock_db, "abc123", "https://x.com")


@pytest.mark.asyncio
@patch("app.services.url.handler.get_url_by_long_url")
async def test_create_or_get_short_url_existing(mock_get_by_long, mock_db):
    fake_url = URL(id=1, slug="oldslug", long_url="https://x.com")
    mock_get_by_long.return_value = fake_url

    result = await service.create_or_get_short_url(mock_db, "https://x.com")
    assert result.slug == "oldslug"
    mock_get_by_long.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.url.handler.get_slug_sequence")
@patch("app.services.url.handler.set_slug_sequence")
async def test_generate_slug_with_sequence(mock_set, mock_get, mock_db):
    mock_get.return_value = SlugSequence(id=1, current_value=100)
    slug = await service.generate_slug_with_sequence(mock_db)
    assert isinstance(slug, str)
    mock_set.assert_awaited_once_with(mock_db, 101)


@pytest.mark.asyncio
@patch("app.services.url.get_cache")
@patch("app.services.url.handler.get_url_by_slug")
@patch("app.services.url.handler.create_visit")
@patch("app.services.url.set_cache")
@patch("app.services.url.delete_cache")
async def test_resolve_slug_cache_hit(
    mock_delete_cache,
    mock_set_cache,
    mock_create_visit,
    mock_get_by_slug,
    mock_get_cache,
    mock_db
):
    cached = {"id": 1, "slug": "abc123", "long_url": "https://x.com"}
    mock_get_cache.return_value = cached

    url = await service.resolve_slug_and_record_visit(mock_db, "abc123")

    assert url.slug == "abc123"
    mock_create_visit.assert_awaited_once_with(mock_db, 1)
    mock_delete_cache.assert_awaited_once_with(TOP_N_SLUG_CACHE_KEY)
    mock_get_by_slug.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.url.get_cache")
@patch("app.services.url.handler.get_url_by_slug")
@patch("app.services.url.handler.create_visit")
@patch("app.services.url.set_cache")
@patch("app.services.url.delete_cache")
async def test_resolve_slug_cache_miss(
    mock_delete_cache,
    mock_set_cache,
    mock_create_visit,
    mock_get_by_slug,
    mock_get_cache,
    mock_db
):
    mock_get_cache.return_value = None
    fake_url = URL(id=1, slug="abc123", long_url="https://x.com")
    mock_get_by_slug.return_value = fake_url

    result = await service.resolve_slug_and_record_visit(mock_db, "abc123")

    assert result.slug == "abc123"
    mock_create_visit.assert_awaited_once_with(mock_db, 1)
    mock_set_cache.assert_awaited_once()
    mock_delete_cache.assert_awaited_once_with(TOP_N_SLUG_CACHE_KEY)
