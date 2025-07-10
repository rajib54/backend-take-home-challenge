import pytest
from unittest.mock import create_autospec
from sqlalchemy.exc import SQLAlchemyError
from app.handler import url as handler
from app.models.urls import URL
from app.models.visit import Visit
from app.models.sequence import SlugSequence
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    return create_autospec(Session)


def test_get_url_by_slug_success(mock_db):
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value.first.return_value = URL(id=1, slug="abc123", long_url="https://x.com")
    
    result = handler.get_url_by_slug(mock_db, "abc123")

    assert isinstance(result, URL)
    assert result.slug == "abc123"


def test_get_url_by_slug_db_error(mock_db):
    mock_db.query.side_effect = SQLAlchemyError("DB failure")
    with pytest.raises(RuntimeError, match="Database error while fetching slug"):
        handler.get_url_by_slug(mock_db, "abc123")


def test_create_url_success(mock_db):
    url = handler.create_url(mock_db, "slugX", "https://example.com")
    
    assert isinstance(url, URL)
    assert url.slug == "slugX"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(url)


def test_create_url_db_error(mock_db):
    mock_db.commit.side_effect = SQLAlchemyError("fail")
    with pytest.raises(RuntimeError, match="Database error while creating URL"):
        handler.create_url(mock_db, "slug", "https://x.com")
    mock_db.rollback.assert_called_once()


def test_create_visit_success(mock_db):
    visit = handler.create_visit(mock_db, url_id=1)
    
    assert isinstance(visit, Visit)
    assert visit.url_id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_visit_db_error(mock_db):
    mock_db.commit.side_effect = SQLAlchemyError("fail")
    with pytest.raises(RuntimeError, match="Database error while creating visit"):
        handler.create_visit(mock_db, url_id=1)
    mock_db.rollback.assert_called_once()


def test_get_slug_sequence_without_lock(mock_db):
    mock_seq = SlugSequence(id=1, current_value=42)
    mock_db.query.return_value.first.return_value = mock_seq

    result = handler.get_slug_sequence(mock_db)
    assert result.current_value == 42


def test_get_slug_sequence_with_lock(mock_db):
    mock_seq = SlugSequence(id=1, current_value=99)
    mock_query = mock_db.query.return_value
    mock_query.with_for_update.return_value.first.return_value = mock_seq

    result = handler.get_slug_sequence(mock_db, lock=True)
    assert result.current_value == 99


def test_set_slug_sequence_update(mock_db):
    mock_existing = SlugSequence(id=1, current_value=42)
    mock_db.query.return_value.first.return_value = mock_existing

    result = handler.set_slug_sequence(mock_db, 100)
    assert result.current_value == 100
    mock_db.commit.assert_called_once()


def test_set_slug_sequence_create(mock_db):
    mock_db.query.return_value.first.return_value = None

    result = handler.set_slug_sequence(mock_db, 1)
    assert result.current_value == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
