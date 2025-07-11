from sqlalchemy.ext.asyncio import AsyncSession
from app.handler import report as report_handler
from app.schemas.schemas import URLStats
from typing import List
from app.services.const import TOP_N_SLUG_CACHE_KEY
from app.utils.cache import get_cache, set_cache

async def get_url_stats(db: AsyncSession, slug: str) -> URLStats:
    """Service: Get detailed stats for a specific slug."""
    return await report_handler.get_stats_for_slug(db, slug)

async def get_top_urls(db: AsyncSession, limit: int = 10) -> List[URLStats]:
    """Service: Get top visited slugs. If it is found in cache serve from there"""
    cached = await get_cache(TOP_N_SLUG_CACHE_KEY)
    if cached and isinstance(cached, list):
        return [URLStats(**item) for item in cached]

    # Fallback to DB
    results = await report_handler.get_top_urls(db, limit)
    data = [
        URLStats(
            slug=row.slug,
            long_url=row.long_url,
            visits=row.visits,
            last_visit=row.last_visit,
        )
        for row in results
    ]

    await set_cache(TOP_N_SLUG_CACHE_KEY, [d.model_dump() for d in data])
    return data
