import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.handler import report as handler
from sqlalchemy.engine import Result


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_get_stats_for_slug_success(mock_db):
    expected_row = ("abc123", "https://example.com", 10, "2024-01-01T12:00:00Z")

    mock_result = MagicMock(spec=Result)
    mock_result.first.return_value = expected_row
    mock_db.execute.return_value = mock_result

    result = await handler.get_stats_for_slug(mock_db, "abc123")

    assert result == expected_row
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_stats_for_slug_db_error(mock_db):
    mock_db.execute.side_effect = SQLAlchemyError("db failed")
    with pytest.raises(RuntimeError, match="Database error while retrieving stats"):
        await handler.get_stats_for_slug(mock_db, "abc123")


@pytest.mark.asyncio
async def test_get_top_urls_success(mock_db):
    expected_rows = [
        ("abc123", "https://example.com", 10, "2024-01-01T12:00:00Z"),
        ("xyz789", "https://xyz.com", 5, "2024-01-02T09:00:00Z"),
    ]

    mock_result = MagicMock(spec=Result)
    mock_result.all.return_value = expected_rows
    mock_db.execute.return_value = mock_result

    result = await handler.get_top_urls(mock_db, limit=5)

    assert result == expected_rows
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_top_urls_db_error(mock_db):
    mock_db.execute.side_effect = SQLAlchemyError("bad db")
    with pytest.raises(RuntimeError, match="Database error while retrieving top URLs"):
        await handler.get_top_urls(mock_db, limit=5)
