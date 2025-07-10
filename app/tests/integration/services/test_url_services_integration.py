from app.services import url as url_service
from app.handler import url as handler


def test_create_or_get_short_url_first_time(test_db):
    long_url = "https://integration.com"
    
    result = url_service.create_or_get_short_url(test_db, long_url)
    
    assert result is not None
    assert result.long_url == long_url
    assert len(result.slug) == 7


def test_create_or_get_short_url_existing(test_db):
    long_url = "https://dupe.com"
    created = url_service.create_or_get_short_url(test_db, long_url)

    # Calling again should return same slug
    existing = url_service.create_or_get_short_url(test_db, long_url)

    assert created.slug == existing.slug
    assert existing.long_url == long_url


def test_generate_slug_with_sequence_increments(test_db):
    handler.set_slug_sequence(test_db, 100)
    slug1 = url_service.generate_slug_with_sequence(test_db)
    slug2 = url_service.generate_slug_with_sequence(test_db)

    assert slug1 != slug2


def test_resolve_slug_and_record_visit(test_db):
    long_url = "https://resolve.com"
    url = url_service.create_or_get_short_url(test_db, long_url)

    # First visit (not cached)
    resolved = url_service.resolve_slug_and_record_visit(test_db, url.slug)
    assert resolved is not None
    assert resolved.slug == url.slug

    # Check visit was recorded
    visits = test_db.query(handler.Visit).filter_by(url_id=url.id).count()
    assert visits == 1


def test_resolve_slug_and_record_visit_not_found(test_db):
    result = url_service.resolve_slug_and_record_visit(test_db, "nonexistent")
    assert result is None
