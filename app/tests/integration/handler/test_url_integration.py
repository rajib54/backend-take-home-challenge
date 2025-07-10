from app.handler import url as handler

def test_create_and_get_url_by_slug(test_db):
    created = handler.create_url(test_db, "abc123", "https://example.com")
    assert created.slug == "abc123"

    fetched = handler.get_url_by_slug(test_db, "abc123")
    assert fetched is not None
    assert fetched.long_url == "https://example.com"


def test_create_and_get_url_by_long_url(test_db):
    handler.create_url(test_db, "xyz", "https://x.com")
    result = handler.get_url_by_long_url(test_db, "https://x.com")
    assert result.slug == "xyz"


def test_create_visit(test_db):
    url = handler.create_url(test_db, "slugX", "https://visit.com")
    visit = handler.create_visit(test_db, url_id=url.id)
    assert visit.url_id == url.id


def test_slug_sequence_set_and_get(test_db):
    # Set sequence to 10
    handler.set_slug_sequence(test_db, 10)
    seq = handler.get_slug_sequence(test_db)
    assert seq.current_value == 10

    # Update to 20
    handler.set_slug_sequence(test_db, 20)
    seq2 = handler.get_slug_sequence(test_db)
    assert seq2.current_value == 20


def test_get_slug_sequence_with_lock(test_db):
    # This should behave like get_slug_sequence
    handler.set_slug_sequence(test_db, 42)
    result = handler.get_slug_sequence(test_db, lock=True)
    assert result.current_value == 42
