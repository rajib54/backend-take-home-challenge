import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.handler import url as handler
from app.models.urls import URL
from app.models.visit import Visit
from app.models.sequence import SlugSequence
from sqlalchemy.engine import Result


@pytest.fixture
def mock_db():
    """Fixture to create a mock AsyncSession."""
    db = AsyncMock(spec=AsyncSession)
    return db

@pytest.mark.asyncio
async def test_get_url_by_slug_success(mock_db):
    url = URL(id=1, slug="abc123", long_url="https://x.com")
    result_mock = MagicMock(spec=Result)
    result_mock.scalar_one_or_none.return_value = url
    mock_db.execute.return_value = result_mock

    result = await handler.get_url_by_slug(mock_db, "abc123")
    assert isinstance(result, URL)
    assert result.slug == "abc123"

@pytest.mark.asyncio
async def test_get_url_by_slug_db_error(mock_db):
    mock_db.execute.side_effect = SQLAlchemyError("DB failure")
    with pytest.raises(RuntimeError, match="Database error while fetching slug"):
        await handler.get_url_by_slug(mock_db, "abc123")


@pytest.mark.asyncio
async def test_create_url_success(mock_db):
    url = await handler.create_url(mock_db, "slugX", "https://example.com")

    assert isinstance(url, URL)
    assert url.slug == "slugX"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(url)

@pytest.mark.asyncio
async def test_create_url_db_error(mock_db):
    mock_db.commit.side_effect = SQLAlchemyError("fail")
    with pytest.raises(RuntimeError, match="Database error while creating URL"):
        await handler.create_url(mock_db, "slug", "https://x.com")
    mock_db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_visit_success(mock_db):
    visit = await handler.create_visit(mock_db, url_id=1)

    assert isinstance(visit, Visit)
    assert visit.url_id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_visit_db_error(mock_db):
    mock_db.commit.side_effect = SQLAlchemyError("fail")
    with pytest.raises(RuntimeError, match="Database error while creating visit"):
        await handler.create_visit(mock_db, url_id=1)
    mock_db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_slug_sequence_without_lock(mock_db):
    slug_seq = SlugSequence(id=1, current_value=42)
    result_mock = MagicMock(spec=Result)
    result_mock.scalar_one_or_none.return_value = slug_seq
    mock_db.execute.return_value = result_mock

    result = await handler.get_slug_sequence(mock_db)
    assert result.current_value == 42


@pytest.mark.asyncio
async def test_get_slug_sequence_with_lock(mock_db):
    slug_seq = SlugSequence(id=1, current_value=99)
    result_mock = MagicMock(spec=Result)
    result_mock.scalar_one_or_none.return_value = slug_seq
    mock_db.execute.return_value = result_mock

    result = await handler.get_slug_sequence(mock_db, lock=True)
    assert result.current_value == 99


@pytest.mark.asyncio
async def test_set_slug_sequence_update(mock_db):
    existing = SlugSequence(id=1, current_value=42)
    result_mock = MagicMock(spec=Result)
    result_mock.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = result_mock

    result = await handler.set_slug_sequence(mock_db, 100)
    assert result.current_value == 100
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_set_slug_sequence_create(mock_db):
    result_mock = MagicMock(spec=Result)
    result_mock.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = result_mock

    result = await handler.set_slug_sequence(mock_db, 1)
    assert result.current_value == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
