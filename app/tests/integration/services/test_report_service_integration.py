from app.services import report as report_service
from app.services import url as url_service
from app.handler import url as handler


def test_get_url_stats_returns_correct_data(test_db):
    # Create and visit a URL
    url = url_service.create_or_get_short_url(test_db, "https://stat.com")
    for _ in range(3):
        handler.create_visit(test_db, url.id)

    stats = report_service.get_url_stats(test_db, url.slug)

    assert stats is not None
    assert stats.slug == url.slug
    assert stats.long_url == url.long_url
    assert stats.visits == 3
    assert stats.last_visit is not None


def test_get_url_stats_returns_none_if_slug_missing(test_db):
    stats = report_service.get_url_stats(test_db, "missing-slug")
    assert stats is None


def test_get_top_urls_returns_most_visited(test_db):
    # Setup
    url1 = url_service.create_or_get_short_url(test_db, "https://top1.com")
    url2 = url_service.create_or_get_short_url(test_db, "https://top2.com")

    for _ in range(5):
        handler.create_visit(test_db, url2.id)
    for _ in range(2):
        handler.create_visit(test_db, url1.id)

    top_urls = report_service.get_top_urls(test_db, limit=2)

    assert len(top_urls) == 2
    assert top_urls[0].slug == url2.slug
    assert top_urls[0].visits == 5
    assert top_urls[1].slug == url1.slug
    assert top_urls[1].visits == 2


def test_get_top_urls_returns_empty_when_no_data(test_db):
    result = report_service.get_top_urls(test_db)
    assert result == []
