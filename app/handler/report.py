from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.exc import SQLAlchemyError
from app.models.urls import URL
from app.models.visit import Visit
import logging

logger = logging.getLogger(__name__)

def get_stats_for_slug(db: Session, slug: str):
    """Return visit stats for a specific slug: total count and most recent visit."""
    try:
        return db.query(
            URL.slug,
            URL.long_url,
            func.count(Visit.id).label('visits'),
            func.max(Visit.timestamp).label('last_visit')
        ).join(Visit).filter(URL.slug == slug).group_by(URL.id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching stats for slug '{slug}': {e}")
        raise RuntimeError("Database error while retrieving stats")

def get_top_urls(db: Session, limit: int = 10):
    """Return top visited slugs, ordered by visit count."""
    try:
        return db.query(
            URL.slug,
            URL.long_url,
            func.count(Visit.id).label('visits'),
            func.max(Visit.timestamp).label('last_visit')
        ).join(Visit).group_by(URL.id).order_by(desc('visits')).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching top {limit} URLs: {e}")
        raise RuntimeError("Database error while retrieving top URLs")
