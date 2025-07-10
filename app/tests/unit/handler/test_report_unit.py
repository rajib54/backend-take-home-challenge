import pytest
from unittest.mock import create_autospec, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.handler import report as handler


@pytest.fixture
def mock_db():
    return create_autospec(Session)


def test_get_stats_for_slug_success(mock_db):
    expected_result = ("abc123", "https://example.com", 10, "2024-01-01T12:00:00Z")

    # Set up mock query chain
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.first.return_value = expected_result

    result = handler.get_stats_for_slug(mock_db, "abc123")

    assert result == expected_result
    mock_db.query.assert_called_once()


def test_get_stats_for_slug_db_error(mock_db):
    mock_db.query.side_effect = SQLAlchemyError("db failed")
    with pytest.raises(RuntimeError, match="Database error while retrieving stats"):
        handler.get_stats_for_slug(mock_db, "abc123")


def test_get_top_urls_success(mock_db):
    expected_result = [
        ("abc123", "https://example.com", 10, "2024-01-01T12:00:00Z"),
        ("xyz789", "https://xyz.com", 5, "2024-01-02T09:00:00Z"),
    ]

    # Set up mock query chain
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = expected_result

    result = handler.get_top_urls(mock_db, limit=5)

    assert result == expected_result
    mock_db.query.assert_called_once()


def test_get_top_urls_db_error(mock_db):
    mock_db.query.side_effect = SQLAlchemyError("bad db")
    with pytest.raises(RuntimeError, match="Database error while retrieving top URLs"):
        handler.get_top_urls(mock_db, limit=5)
