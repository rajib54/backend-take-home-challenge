from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.urls import URL
from app.models.visit import Visit
from app.models.sequence import SlugSequence
import logging

logger = logging.getLogger(__name__)

async def get_url_by_slug(db: AsyncSession, slug: str) -> URL | None:
    """Retrieve a URL object by its slug."""
    try:
        result = await db.execute(select(URL).where(URL.slug == slug))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching slug '{slug}': {e}")
        raise RuntimeError("Database error while fetching slug")

async def get_url_by_long_url(db: AsyncSession, long_url: str) -> URL | None:
    """Retrieve a URL object by its original long URL."""
    try:
        result = await db.execute(select(URL).where(URL.long_url == long_url))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching long_url '{long_url}': {e}")
        raise RuntimeError("Database error while fetching long URL")

async def create_url(db: AsyncSession, slug: str, long_url: str) -> URL:
    """Create a new URL object."""
    try:
        db_url = URL(slug=slug, long_url=long_url)
        db.add(db_url)
        await db.commit()
        await db.refresh(db_url)
        return db_url
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Error creating URL for slug '{slug}': {e}")
        raise RuntimeError("Database error while creating URL")

async def create_visit(db: AsyncSession, url_id: int) -> Visit:
    """Create a visit record for a given URL."""
    try:
        visit = Visit(url_id=url_id)
        db.add(visit)
        await db.commit()
        return visit
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Error logging visit for url_id '{url_id}': {e}")
        raise RuntimeError("Database error while creating visit")

async def get_slug_sequence(db: AsyncSession, lock: bool = False) -> SlugSequence | None:
    """Fetch the current slug sequence, with optional row locking."""
    try:
        stmt = select(SlugSequence)
        if lock:
            stmt = stmt.with_for_update()
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching slug sequence: {e}")
        raise RuntimeError("Database error while fetching slug sequence")

async def set_slug_sequence(db: AsyncSession, value: int) -> SlugSequence:
    """Update or initialize the slug sequence counter."""
    try:
        result = await db.execute(select(SlugSequence))
        record = result.scalar_one_or_none()
        if record:
            record.current_value = value
        else:
            record = SlugSequence(current_value=value)
            db.add(record)
        await db.commit()
        return record
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Error setting slug sequence to {value}: {e}")
        raise RuntimeError
