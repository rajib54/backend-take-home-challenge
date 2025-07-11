from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models.urls import URL
from app.models.visit import Visit
import logging

logger = logging.getLogger(__name__)

async def get_stats_for_slug(db: AsyncSession, slug: str):
    """Return visit stats for a specific slug: total count and most recent visit."""
    try:
        stmt = (
            select(
                URL.slug,
                URL.long_url,
                func.count(Visit.id).label('visits'),
                func.max(Visit.timestamp).label('last_visit')
            )
            .join(Visit)
            .where(URL.slug == slug)
            .group_by(URL.id)
        )
        result = await db.execute(stmt)
        return result.first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching stats for slug '{slug}': {e}")
        raise RuntimeError("Database error while retrieving stats")

async def get_top_urls(db: AsyncSession, limit: int = 10):
    """Return top visited slugs, ordered by visit count."""
    try:
        stmt = (
            select(
                URL.slug,
                URL.long_url,
                func.count(Visit.id).label('visits'),
                func.max(Visit.timestamp).label('last_visit')
            )
            .join(Visit)
            .group_by(URL.id)
            .order_by(desc('visits'))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching top {limit} URLs: {e}")
        raise RuntimeError("Database error while retrieving top URLs")
