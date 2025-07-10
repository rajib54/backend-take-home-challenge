from unittest.mock import patch, MagicMock, ANY
from app.services import url as url_service
from app.models.urls import URL

def test_int_to_base62_basic():
    slug = url_service.int_to_base62(123456)
    assert len(slug) == 7


@patch("app.services.url.handler")
def test_generate_slug_with_sequence(mock_handler):
    # Setup mock sequence
    mock_handler.get_slug_sequence.return_value = MagicMock(current_value=10)
    mock_handler.set_slug_sequence.return_value = None

    slug = url_service.generate_slug_with_sequence(db=MagicMock())
    assert isinstance(slug, str)
    assert len(slug) == 7

    # Check sequence update
    mock_handler.set_slug_sequence.assert_called_with(ANY, 11)


@patch("app.services.url.handler")
def test_create_or_get_short_url_existing(mock_handler):
    fake_url = URL(id=1, slug="abc123", long_url="https://test.com")
    mock_handler.get_url_by_long_url.return_value = fake_url

    result = url_service.create_or_get_short_url(db=MagicMock(), long_url="https://test.com")

    assert result is fake_url
    mock_handler.create_url.assert_not_called()


@patch("app.services.url.handler")
def test_create_or_get_short_url_new(mock_handler):
    # Simulate no existing entry
    mock_handler.get_url_by_long_url.return_value = None
    mock_handler.get_slug_sequence.return_value = MagicMock(current_value=1)
    mock_handler.set_slug_sequence.return_value = None

    created = URL(id=99, slug="abc999", long_url="https://example.com")
    mock_handler.create_url.return_value = created

    result = url_service.create_or_get_short_url(db=MagicMock(), long_url="https://example.com")

    assert result is created
    mock_handler.create_url.assert_called_once()


@patch("app.services.url.set_cache")
@patch("app.services.url.get_cache")
@patch("app.services.url.handler")
def test_resolve_slug_and_record_visit_cache_hit(mock_handler, mock_get_cache, mock_set_cache):
    # Simulate cache hit
    mock_get_cache.return_value = {
        "id": 1, "slug": "slug1", "long_url": "https://cached.com"
    }

    result = url_service.resolve_slug_and_record_visit(db=MagicMock(), slug="slug1")

    assert result.id == 1
    assert result.slug == "slug1"
    assert result.long_url == "https://cached.com"
    mock_handler.get_url_by_slug.assert_not_called()
    mock_handler.create_visit.assert_called_once_with(ANY, 1)


@patch("app.services.url.set_cache")
@patch("app.services.url.get_cache")
@patch("app.services.url.handler")
def test_resolve_slug_and_record_visit_db_fallback(mock_handler, mock_get_cache, mock_set_cache):
    mock_get_cache.return_value = None

    # Simulate DB fallback
    db_url = URL(id=2, slug="dbslug", long_url="https://db.com")
    mock_handler.get_url_by_slug.return_value = db_url

    result = url_service.resolve_slug_and_record_visit(db=MagicMock(), slug="dbslug")

    assert result == db_url
    mock_handler.create_visit.assert_called_once_with(ANY, 2)
    mock_set_cache.assert_called_once()
    mock_handler.get_url_by_slug.assert_called_once_with(ANY, "dbslug")


@patch("app.services.url.get_cache")
@patch("app.services.url.handler")
def test_resolve_slug_and_record_visit_not_found(mock_handler, mock_get_cache):
    mock_get_cache.return_value = None
    mock_handler.get_url_by_slug.return_value = None

    result = url_service.resolve_slug_and_record_visit(db=MagicMock(), slug="notfound")

    assert result is None
    mock_handler.create_visit.assert_not_called()
