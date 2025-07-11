from sqlalchemy.ext.asyncio import AsyncSession
from app.handler import url as handler
from app.models.urls import URL
from app.utils.cache import get_cache, set_cache, delete_cache
from app.services.const import SLUG_CACHE_KEY_TEMPLATE, TOP_N_SLUG_CACHE_KEY

def int_to_base62(n: int) -> str:
    if n < 0 or n >= 62**6:
        raise ValueError("Number out of range for 6-character Base62 encoding")

    base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = 62
    fancy_padding = "a1b2c3d4e5f"

    result = []
    while n > 0:
        n, rem = divmod(n, base)
        result.append(base62_chars[rem])
    base62_encoded = ''.join(reversed(result))

    pad_len = 6 - len(base62_encoded)
    padded = fancy_padding[:pad_len] + base62_encoded
    checksum_value = sum(ord(c) for c in padded) % base
    checksum_char = base62_chars[checksum_value]

    return padded + checksum_char

async def generate_slug_with_sequence(db: AsyncSession) -> str:
    sequence = await handler.get_slug_sequence(db, lock=True)
    next_value = 1 if not sequence else sequence.current_value + 1
    slug = int_to_base62(next_value)
    await handler.set_slug_sequence(db, next_value)
    return slug

async def create_or_get_short_url(db: AsyncSession, long_url: str) -> URL:
    existing = await handler.get_url_by_long_url(db, long_url)
    if existing:
        return existing

    try:
        slug = await generate_slug_with_sequence(db)
        return await handler.create_url(db, slug, long_url)
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"Failed to create short URL: {e}")

async def resolve_slug_and_record_visit(db: AsyncSession, slug: str) -> URL | None:
    cache_key = SLUG_CACHE_KEY_TEMPLATE.format(slug)
    cached = await get_cache(cache_key)
    if cached:
        await handler.create_visit(db, cached["id"])
        await delete_cache(TOP_N_SLUG_CACHE_KEY)
        return URL(id=cached["id"], slug=cached["slug"], long_url=cached["long_url"])

    url = await handler.get_url_by_slug(db, slug)
    if url:
        await handler.create_visit(db, url.id)
        await set_cache(cache_key, {
            "id": url.id,
            "slug": url.slug,
            "long_url": url.long_url
        }, ttl=60*60*24)
        await delete_cache(TOP_N_SLUG_CACHE_KEY)
    return url
