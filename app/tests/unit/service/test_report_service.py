import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import URLStats
from app.services import report as service


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
@patch("app.services.report.report_handler.get_stats_for_slug")
async def test_get_url_stats(mock_handler, mock_db):
    expected = URLStats(
        slug="abc123", long_url="https://example.com", visits=5, last_visit="2024-01-01T00:00:00"
    )
    mock_handler.return_value = expected

    result = await service.get_url_stats(mock_db, "abc123")
    assert isinstance(result, URLStats)
    assert result.slug == "abc123"
    mock_handler.assert_awaited_once_with(mock_db, "abc123")


@pytest.mark.asyncio
@patch("app.services.report.get_cache")
@patch("app.services.report.report_handler.get_top_urls")
@patch("app.services.report.set_cache")
async def test_get_top_urls_cache_hit(mock_set_cache, mock_get_top_urls, mock_get_cache, mock_db):
    cached_data = [
        {
            "slug": "slug1",
            "long_url": "https://1.com",
            "visits": 10,
            "last_visit": "2024-01-01T00:00:00",
        },
        {
            "slug": "slug2",
            "long_url": "https://2.com",
            "visits": 5,
            "last_visit": "2024-01-02T00:00:00",
        },
    ]
    mock_get_cache.return_value = cached_data

    result = await service.get_top_urls(mock_db)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].slug == "slug1"
    mock_get_top_urls.assert_not_called()
    mock_set_cache.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.report.get_cache")
@patch("app.services.report.report_handler.get_top_urls")
@patch("app.services.report.set_cache")
async def test_get_top_urls_cache_miss(mock_set_cache, mock_get_top_urls, mock_get_cache, mock_db):
    mock_get_cache.return_value = None

    row1 = MagicMock()
    row1.slug = "slug1"
    row1.long_url = "https://1.com"
    row1.visits = 10
    row1.last_visit = "2024-01-01T00:00:00"

    row2 = MagicMock()
    row2.slug = "slug2"
    row2.long_url = "https://2.com"
    row2.visits = 5
    row2.last_visit = "2024-01-02T00:00:00"

    mock_get_top_urls.return_value = [row1, row2]

    result = await service.get_top_urls(mock_db, limit=2)
    assert len(result) == 2
    assert result[0].slug == "slug1"
    mock_get_top_urls.assert_awaited_once_with(mock_db, 2)
    mock_set_cache.assert_awaited_once()
