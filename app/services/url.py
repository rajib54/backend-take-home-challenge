
from sqlalchemy.orm import Session
from app.handler import url as handler
from app.models.urls import URL
from app.utils.cache import get_cache, set_cache

def int_to_base62(n: int) -> str:
    """
    Convert an integer to a 7-character Base62 string:
    - 6 characters for Base62-encoded number (with alphabet+digit padding)
    - 1 character checksum
    """
    if n < 0 or n >= 62**6:
        raise ValueError("Number out of range for 6-character Base62 encoding")

    base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = 62
    fancy_padding = "a1b2c3d4e5f"  # Must be long enough for 6-character padding

    # Step 1: Base62 encode (up to 6 characters)
    result = []
    while n > 0:
        n, rem = divmod(n, base)
        result.append(base62_chars[rem])
    base62_encoded = ''.join(reversed(result))

    # Step 2: Replace leading padding with non-zero mix
    pad_len = 6 - len(base62_encoded)
    padded = fancy_padding[:pad_len] + base62_encoded  # Custom padding

    # Step 3: Compute checksum
    checksum_value = sum(ord(c) for c in padded) % base
    checksum_char = base62_chars[checksum_value]

    return padded + checksum_char



def generate_slug_with_sequence(db: Session) -> str:
    """Generate a unique base62 slug using a DB-backed sequence counter."""
    sequence = handler.get_slug_sequence(db, lock=True)
    next_value = 1 if not sequence else sequence.current_value + 1
    slug = int_to_base62(next_value)
    handler.set_slug_sequence(db, next_value)
    return slug

def create_or_get_short_url(db, long_url: str) -> URL:
    """Check if a long URL has been shortened already; otherwise create one."""
    existing = handler.get_url_by_long_url(db, long_url)
    if existing:
        return existing

    try:
        slug = generate_slug_with_sequence(db)
        return handler.create_url(db, slug, long_url)
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to create short URL: {e}")

def resolve_slug_and_record_visit(db, slug: str) -> URL | None:
    """Resolve slug to URL with Redis caching and avoid DB hit when cached."""
    cache_key_template = "slug:{}"
    cache_key = cache_key_template.format(slug)
    cached = get_cache(cache_key)
    if cached:
        # No DB fetch needed, create_visit directly using cached ID
        handler.create_visit(db, cached["id"])
        return URL(id=cached["id"], slug=cached["slug"], long_url=cached["long_url"])

    # Fallback to DB
    url = handler.get_url_by_slug(db, slug)
    if url:
        handler.create_visit(db, url.id)
        # set to cache for one day
        set_cache(cache_key, {
            "id": url.id,
            "slug": url.slug,
            "long_url": url.long_url
        }, ttl=60*60*24)
    return url
