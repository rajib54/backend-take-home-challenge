from app.handler.report import get_stats_for_slug, get_top_urls
from app.handler.url import create_url, create_visit

def test_get_stats_for_slug(test_db):
    # Setup test data
    url = create_url(test_db, "testslug", "https://test.com")
    create_visit(test_db, url_id=url.id)
    create_visit(test_db, url_id=url.id)

    # Run report function
    stats = get_stats_for_slug(test_db, "testslug")

    assert stats is not None
    assert stats.slug == "testslug"
    assert stats.long_url == "https://test.com"
    assert stats.visits == 2
    assert stats.last_visit is not None


def test_get_stats_for_slug_no_visits(test_db):
    # Setup test data
    create_url(test_db, "novisits", "https://empty.com")

    # Run report function
    stats = get_stats_for_slug(test_db, "novisits")

    # Should return None because no visits joined
    assert stats is None


def test_get_top_urls(test_db):
    # Setup multiple URLs with different visit counts
    url1 = create_url(test_db, "slug1", "https://site1.com")
    url2 = create_url(test_db, "slug2", "https://site2.com")

    # Add visits
    for _ in range(3):
        create_visit(test_db, url_id=url1.id)

    for _ in range(5):
        create_visit(test_db, url_id=url2.id)

    top_urls = get_top_urls(test_db, limit=5)

    assert len(top_urls) >= 2
    assert top_urls[0].slug == "slug2"
    assert top_urls[0].visits == 5
    assert top_urls[1].slug == "slug1"
    assert top_urls[1].visits == 3


def test_get_top_urls_empty(test_db):
    # Nothing in DB
    result = get_top_urls(test_db)
    assert result == []
